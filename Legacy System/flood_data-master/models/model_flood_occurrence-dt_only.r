
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


cols_to_remove = c('level_0', 'index', 'is_dntn', 'flood_pt', 'event_name', 'num_flooded', 'location', 'count', 'flooded', 'in_hague')
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

dt_fmla = as.formula(paste(out_col_name, "~", paste(in_col_names, collapse="+")))

colnames(train_data)

fit = rpart(dt_fmla, method='class', data=train_data, minsplit=1, minbucket=1)
printcp(fit)

tiff(paste(fig_dir, "Plot_hg.tif"), width=9, height=6, units='in', res = 300)
rpart.plot(fit, under=TRUE, cex=0.9, extra=1, varlen = 6)
dev.off()
rpart.plot(fit, under=TRUE, cex=0.9, extra=1, varlen = 6)

pfit<- prune(fit, cp=fit$cptable[which.min(fit$cptable[,"xerror"]),"CP"])
rpart.plot(pfit, under=TRUE, cex=0.8, extra=1, varlen = 6)

pred = predict(pfit, train_data, type = 'class')
table(trn_out, pred)

pred = predict(pfit, test_data, type = 'class')
table(tst_out, pred)


