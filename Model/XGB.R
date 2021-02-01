# Load Libraries
library(xgboost)
library(Matrix)
library(tidyverse)
library(data.table)
library(scales)
library(MLmetrics)

# read data
data <- read_csv("data.csv")

# Split data into train and test
set.seed(1234)
ind <- sample(2, nrow(data), replace = T, prob = c(.7, .3))
train <- data[ind == 1, 1:6]
test <- data[ind == 2, 1:6]

# Dataframe to data table 
t_train <- setDT(train)
t_test <- setDT(test)

# Create predictive variable 
labels <- data[ind == 1, 7]
ts_labels <- data[ind == 2, 7]

# dataframe to numeric
ts_labels <- ts_labels$dust
labels <- labels$dust

# Convert into Matrix
dtrain <- xgb.DMatrix(label = labels, data = as.matrix(train))
dtest <- xgb.DMatrix(label = ts_labels, data = as.matrix(test))

# XGBoost Model |You can change parameters based on your data|
xgb_new <- xgboost(data = dtrain,
                   label = labels,
                   trees = 1000,
                   mtry = 8,
                   min_n = 10,
                   tree_depth = 3,
                   learn_rate= 	0.00644471,
                   loss_reduction = 0.000002150994,
                   sample_size = 0.4017052,
                   eval_metric ="rmse",
                   nrounds = 1000)

# Properties
print(xgb_new)

# Actual Value vs Predicted Value
pred <- predict(xgb_new, dtest)
RMSE(pred, ts_labels)
aa <- cbind(ts_labels,pred)

# Variable Importance
importance_matrix <- xgb.importance(model = xgb_new)
xgb.plot.importance(importance_matrix = importance_matrix)

# Save model
saveRDS(xgb_new, file = "xgb.rds")
