library(dplyr)
modeling_data <- read.csv("modeling_dataset.csv")
modeling_data$home_spread_cover<-ifelse(modeling_data$home_spread_cover=="True", 1, 0)
modeling_data$qb_backup_home <- ifelse(modeling_data$qb_backup_home=="", "N", modeling_data$qb_backup_home)
modeling_data$qb_backup_away <- ifelse(modeling_data$qb_backup_away=="", "N", modeling_data$qb_backup_away)
wks_2_18 <- modeling_data %>%
  filter(week <=18, week >1)

### Generalized Additive Model ###

library("gam")
predictors <- c('avg_qb_hits_differential_diff', 'avg_turnover_differential_diff' , 'qb_backup_home' ,
                'avg_diff_from_spread_capped_diff', 'prime_time', 'temp_cat', 'distance_bucket')

#Model 1
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ s(avg_qb_hits_differential_diff, df=5) +s(avg_turnover_differential_diff, df=5)+ qb_backup_home
                 +s(avg_diff_from_spread_capped_diff, df=5)+prime_time+temp_cat+distance_bucket
                 , data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .528; Mean: .537

#Model 2
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ s(avg_qb_hits_differential_diff, df=5) +s(avg_turnover_differential_diff, df=5)
                 + qb_backup_home+avg_diff_from_spread_capped_diff+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .532; Mean: .533

#Model 3
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ s(avg_qb_hits_differential_diff, df=5) +avg_turnover_differential_diff
                 + qb_backup_home+s(avg_diff_from_spread_capped_diff, df=5)+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .530; Mean: .535

#Model 4
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ avg_qb_hits_differential_diff +s(avg_turnover_differential_diff,df=5)
                 + qb_backup_home+s(avg_diff_from_spread_capped_diff, df=5)+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .530; Mean: .531

#Model 5
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ s(avg_qb_hits_differential_diff,df=5) +avg_turnover_differential_diff
                 + qb_backup_home+avg_diff_from_spread_capped_diff+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .528; Mean: .539

#Model 6 (Best model)
accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ avg_qb_hits_differential_diff +s(avg_turnover_differential_diff,df=5)
                 + qb_backup_home+avg_diff_from_spread_capped_diff+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector) #Med: .552; Mean: .537
gam_acc_vector <- accuracy_vector

#Model 7

accuracy_vector <- c()
for (yr in unique(modeling_data$year)) {
  gam_data <- na.omit(wks_2_18[ ,c("home_spread_cover", "year", predictors)])
  train <- gam_data[gam_data$year != yr, ]
  test<-gam_data[gam_data$year == yr,] 
  gam.fit <- gam(home_spread_cover ~ avg_qb_hits_differential_diff +avg_turnover_differential_diff
                 + qb_backup_home+s(avg_diff_from_spread_capped_diff,df=5)+prime_time+temp_cat+distance_bucket, data = train, family=binomial)
  gam.probs<-predict(gam.fit, newdata = test, type='response')
  test$pred <- ifelse(gam.probs > 0.5, 1, 0); test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy<-mean(na.omit(test$acc))
  print(accuracy)
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector)#Med: .528; Med: .535