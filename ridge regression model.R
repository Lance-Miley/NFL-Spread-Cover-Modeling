library(dplyr)
library(glmnet)
modeling_data <- read.csv("modeling_dataset.csv")
modeling_data$home_spread_cover<-ifelse(modeling_data$home_spread_cover=="True", 1, 0)
modeling_data$qb_backup_home <- ifelse(modeling_data$qb_backup_home=="", "N", modeling_data$qb_backup_home)
modeling_data$qb_backup_away <- ifelse(modeling_data$qb_backup_away=="", "N", modeling_data$qb_backup_away)
wks_2_18 <- modeling_data %>%
  filter(week <=18, week >1)

### Ridge Regression ###

#Ridge--many predictors
predictors <- c('avg_point_differential_diff','avg_yard_differential_diff','avg_turnover_differential_diff','weighted_dvoa_diff','total_dvoa_rank_diff','avg_diff_from_spread_capped_diff','spread_line',
                "avg_qb_hits_differential_diff", "avg_two_min_differential_diff", 'prime_time', 'temp_cat', 'distance_bucket', 'qb_backup_home' )

accuracy_vector<-c()
for (yr in unique(modeling_data$year)) {
  
  train <- wks_2_18[wks_2_18$year != yr, ]
  train<- na.omit(train[ ,c("home_spread_cover", predictors)])
  test <- wks_2_18[wks_2_18$year == yr, ]
  test<- na.omit(test[ ,c("home_spread_cover", predictors)])
  
  x<-model.matrix(home_spread_cover~., train)[,-1]
  y<-train$home_spread_cover
  
  cv.ridge<- cv.glmnet(x,y, alpha=0, family="binomial")
  
  x_test<-model.matrix(home_spread_cover~., test)[,-1]
  y_test<-test$home_spread_cover
  
  ridge_fit <- glmnet(x,y, alpha = 0, lambda = cv.ridge$lambda.min)
  ridge.probs <- predict(ridge_fit, newx = x_test, type="response")
  test$pred <- ifelse(ridge.probs > 0.5, 1, 0)
  test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector)
ridge_acc_vector <- accuracy_vector



#Ridge--same predictors as logistic
predictors <- c('avg_qb_hits_differential_diff', 'avg_turnover_differential_diff' , 'qb_backup_home' ,
                'avg_diff_from_spread_capped_diff', 'prime_time', 'temp_cat', 'distance_bucket')

accuracy_vector<-c()
for (yr in unique(modeling_data$year)) {
  
  train <- wks_2_18[wks_2_18$year != yr, ]
  train<- na.omit(train[ ,c("home_spread_cover", predictors)])
  test <- wks_2_18[wks_2_18$year == yr, ]
  test<- na.omit(test[ ,c("home_spread_cover", predictors)])
  
  x<-model.matrix(home_spread_cover~., train)[,-1]
  y<-train$home_spread_cover
  
  cv.ridge<- cv.glmnet(x,y, alpha=0, family="binomial")
  
  x_test<-model.matrix(home_spread_cover~., test)[,-1]
  y_test<-test$home_spread_cover
  
  ridge_fit <- glmnet(x,y, alpha = 0, lambda = cv.ridge$lambda.min)
  ridge.probs <- predict(ridge_fit, newx = x_test, type="response")
  test$pred <- ifelse(ridge.probs > 0.5, 1, 0)
  test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
}

summary(accuracy_vector)