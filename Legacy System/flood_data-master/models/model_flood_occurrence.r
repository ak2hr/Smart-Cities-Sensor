
repo = "http://cran.us.r-project.org"
library(caret)
library(ggfortify)
library(ggplot2)
library(dplyr)
library(rpart)
library(rpart.plot)
library(RSQLite)
library(DBI)
library(randomForest)
library(e1071)
library(class)

classify_knn = function(pca.data, obs_data, point, k){
  neighs = get_nn(pca.data, point, k)
  neigh_data = obs_data[neighs,]
  return(names(which.max(table(neigh_data$fld))))
}

get_nn = function(d, point, k){
  point = d[point, ]
  dists = sort(sqrt(rowSums((t(t(d) - point))^2)))
  close_points = names(dists)[2:k]
  return(close_points)
}

remove_cols= function(l, cols){
    return(l[! l %in% cols])
}

make_factors = function(model_data){
model_data$Structure1 = as.factor(model_data$Structure1)
model_data$Pipe_Geome = as.factor(model_data$Pipe_Geome)
model_data$Pipe_Mater = as.factor(model_data$Pipe_Mater)
model_data$Condition = as.factor(model_data$Condition)
return(model_data)
}

base_dir<- "C:/Users/Jeff/Documents/research/Sadler_3rdPaper/manuscript/"
data_dir<- "C:/Users/Jeff/Google Drive/research/Sadler_3rdPaper_Data/"
fig_dir <- paste(base_dir, "Figures/general/", sep="")
db_filename <- "floodData.sqlite"

con = dbConnect(RSQLite::SQLite(), dbname=paste(data_dir, db_filename, sep=""))

test_df = dbReadTable(con, 'test_geog_data_hg')
train_df = dbReadTable(con, 'train_geog_data_hg')

colnames(test_df)


cols_to_remove = c('level_0', 'index', 'is_dntn', 'flood_pt', 'event_name', 'num_flooded', 'location', 'count', 'flooded')
in_col_names = remove_cols(colnames(test_df), cols_to_remove)
out_col_name = 'flooded'

test_df = make_factors(test_df)
train_df = make_factors(train_df)

train_data = train_df[, append(in_col_names, out_col_name)]
test_data = test_df[, append(in_col_names, out_col_name)]

train_in_data = train_df[, in_col_names]
test_in_data = test_df[, in_col_names]

tst_out = test_df[, out_col_name]
trn_out = train_df[, out_col_name]

train_col_stds = apply(train_in_data, 2, sd)
train_col_means = colMeans(train_in_data)

train_normalized = t((t(train_in_data)-train_col_means)/train_col_stds)
test_normalized = t((t(test_in_data)-train_col_means)/train_col_stds)

pca = prcomp(train_normalized)
pca$x = -pca$x
pca$rotation=-pca$rotation
p = ggplot(pca$x[,c(1,2)], aes(x=PC1, y=PC2, colour=model_data[train_ind, out_col_name], label=rownames(pca$x)))
p + geom_point() + geom_text()
print(pca)
plot(pca)

trn_preprocessed = predict(pca, train_normalized)
tst_preprocessed = predict(pca, test_normalized)
trn_in = trn_preprocessed
tst_in = tst_preprocessed

train_data = cbind(as.data.frame(trn_in), flooded = model_data[train_ind, out_col_name])
fmla = as.formula(paste(out_col_name, "~", paste(colnames(trn_in), collapse="+")))
fmla

kfit = knn(trn_in, tst_in, trn_out, k=5)
table(tst_out, kfit)

svm_fit = svm(fmla, data=train_data)
svm_pred = predict(svm_fit, tst_in)
table(tst_out, svm_pred)

dt_fmla = as.formula(paste(out_col_name, "~", paste(in_col_names, collapse="+")))

colnames(train_data)

fit = rpart(dt_fmla, method='class', data=train_data, minsplit=1, minbucket=1)
printcp(fit)

tiff(paste(fig_dir, "Plot_hg.tif"), width=9, height=6, units='in', res = 300)
rpart.plot(fit, under=TRUE, cex=0.9, extra=1, varlen = 6)
dev.off()
rpart.plot(fit, under=TRUE, cex=0.9, extra=1, varlen = 6)

pfit<- prune(fit, cp=fit$cptable[which.min(fit$cptable[,"xerror"]),"CP"])
rpart.plot(pfit, under=TRUE, cex=0.9, extra=1, varlen = 6)

pred = predict(pfit, train_data, type = 'class')
table(trn_out, pred)

pred = predict(pfit, test_data, type = 'class')
table(tst_out, pred)

forest = randomForest(dt_fmla, data = dt_train_data, importance = TRUE, type="classification", nodesize=2)

pred = predict(forest, dt_train_data[, in_col_names])
table(trn_out, pred)

pred = predict(forest, dt_test_data)
table(tst_out, pred)
impo = as.data.frame(forest$importance)
impo = impo[order(-impo$MeanDecreaseGini),]
par(las=2)
barplot(impo$MeanDecreaseGini, names.arg=rownames(impo), ylim = c(0, 70))

lo_fit = glm(fmla, family=binomial(link='logit'), data=train_data)
print(lo_fit)

pred = predict(lo_fit, as.data.frame(tst_in), type="response")
table(tst_out, round(pred)>0)


