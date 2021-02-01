# Load Libraries
library(randomForest)
library(caret)
library(Metrics)
library(tidyverse)

# read data from excel
data <- read_excel("Sensor Data.xlsx")

# Removed First Column |Date Time|
data<- data[,-1]

# Renamed the column names
colnames(data) <- c("mq5","mq9", "mq135", "humidity", "temp","pressure","dust")

# write data into csv file |USE THIS FILE|
write_csv(data,"data.csv")

# Split data into train and test
set.seed(1234)
ind <- sample(2, nrow(data), replace = T, prob = c(.7, .3))
training <- data[ind == 1, ]
test <- data[ind == 2, ]

# change all variable into character -> numeric
data<- data %>% 
  mutate_if(is.character, as.numeric)

# Create A Random Forest model with Default parameters
set.seed(222)
rf <- randomForest(dust ~ ., # if you need to change predictive variable change this!!
                   data = training,
                   mtry = 3,
                   ntree = 500,
                   proximity = F
)

# Properties
summary(rf)
print(rf)

# Actual Value vs Predicted Value
p1 <- predict(rf, test)
pre <- p1
act <- test$dust
t1 <- cbind(pre, act)
RMSE(p1, test$dust) # Lower the RMSE better the model

# Variable Importance
rf$importance
varImpPlot(rf,
           sort = T,
           n.var = 7,
           main ="Feature Importance of Random Forest"
)

# Save model
saveRDS(rf, file = "random_forest.rds")


