
repo = "http://cran.us.r-project.org"
library(caret)
library(ggfortify)
library(ggplot2)
library(dplyr)
library(RSQLite)
library(DBI)
library(class)
library(pscl)

remove_cols= function(l, cols){
    return(l[! l %in% cols])
}

base_dir<- "C:/Users/Jeff/Documents/research/Sadler_3rdPaper/manuscript/"
data_dir<- "C:/Users/Jeff/Google Drive/research/Sadler_3rdPaper_Data/"
fig_dir <- paste(base_dir, "Figures/general/", sep="")
db_filename <- "floodData.sqlite"

con = dbConnect(RSQLite::SQLite(), dbname=paste(data_dir, db_filename, sep=""))

df = dbReadTable(con, 'for_model_avgs')

colnames(df)


cols_to_remove = c('event_name', 'event_date', 'num_flooded')
in_col_names = remove_cols(colnames(df), cols_to_remove)
# in_col_names = c('td_av', 'llt')
out_col_name = 'num_flooded'

model_data = df[, append(in_col_names, out_col_name)]
nrow(model_data)
model_data = na.omit(model_data)
model_data = model_data[model_data[,'rd']>0.01,]
nrow(model_data)
model_data


prt = createDataPartition(model_data[, out_col_name], p=0.7)

train_data = model_data[prt$Resample1,]
train_in_data = model_data[prt$Resample1, in_col_names]
train_out_data = model_data[prt$Resample1, out_col_name]
test_in_data = model_data[-prt$Resample1, in_col_names]
test_out_data = model_data[-prt$Resample1, out_col_name]

train_col_stds = apply(train_in_data, 2, sd)
train_col_means = colMeans(train_in_data)

train_normalized = t((t(train_in_data)-train_col_means)/train_col_stds)
test_normalized = t((t(test_in_data)-train_col_means)/train_col_stds)

pca = prcomp(train_normalized)
pca$x = -pca$x
pca$rotation=-pca$rotation
p = ggplot(pca$x[,c(1,2)], aes(x=PC1, y=PC2, colour=model_data[prt$Resample1, out_col_name], label=rownames(pca$x)))
p + geom_point() + geom_text()

trn_preprocessed = predict(pca, train_normalized)
tst_preprocessed = predict(pca, test_normalized)

fmla = as.formula(paste(out_col_name, "~", paste(colnames(trn_preprocessed), collapse="+")))
fmla

train_data = cbind(as.data.frame(trn_preprocessed), num_flooded = model_data[prt$Resample1, out_col_name])

output = zeroinfl(fmla, data=train_data, family = poisson)

summary(output)

train_fld = train_out_data[train_out_data>0]
pred_trn = predict(output, newdata = as.data.frame(trn_preprocessed), type='response')
pred_trn_capped = replace(pred_trn, pred_trn > 159, 159)
pred_trn_fld = pred_trn_capped[model_data[prt$Resample1, out_col_name]>0]

mean(abs(pred_trn_capped - train_out_data))
mean(abs(train_fld - pred_trn_fld))

max_val = max(max(train_fld), max(pred_trn_fld))

plot(pred_trn_fld, train_fld, asp=1, ylim=c(0,max_val), xlim=c(0,max_val))

test_out_data
test_fld = test_out_data[test_out_data>0]
pred = predict(output, newdata = as.data.frame(tst_preprocessed), type='response')
max(pred)
pred_capped = replace(pred, pred > 159, 159)
pred_fld = pred_capped[model_data[-prt$Resample1, out_col_name]>0]
pred_capped

sort(pred_capped)

mean(abs(pred_capped - test_out_data)^2)
mean(abs(test_fld - pred_fld))

max_val = max(max(test_fld), max(pred_fld))

plot(pred_fld, test_fld, asp=1, ylim=c(0,max_val), xlim=c(0,max_val))

with(output, cbind(res.deviance = deviance, df = df.residual, p = pchisq(deviance, df.residual, lower.tail=FALSE)))
