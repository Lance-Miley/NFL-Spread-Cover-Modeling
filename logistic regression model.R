library(dplyr)
modeling_data <- read.csv("modeling_dataset.csv")
modeling_data$home_spread_cover<-ifelse(modeling_data$home_spread_cover=="True", 1, 0)
modeling_data$qb_backup_home <- ifelse(modeling_data$qb_backup_home=="", "N", modeling_data$qb_backup_home)
modeling_data$qb_backup_away <- ifelse(modeling_data$qb_backup_away=="", "N", modeling_data$qb_backup_away)
wks_2_18 <- modeling_data %>%
  filter(week <=18, week >1)

### Logistic Regression Model ###

accuracy_vector<-c()
test_df <- data.frame(matrix(nrow=0, ncol=11))
colnames(test_df)<-c('week', 'avg_qb_hits_differential_diff', 'avg_turnover_differential_diff' , 'home_spread_cover', 'qb_backup_home' , 'avg_diff_from_spread_capped_diff', 'prime_time', 'temp_cat', 'distance_bucket', 'pred', 'acc')
for (yr in unique(modeling_data$year)) {
  
  train <- wks_2_18[wks_2_18$year != yr, ]
  test<-wks_2_18[wks_2_18$year == yr, ] %>% select(week, avg_qb_hits_differential_diff, avg_turnover_differential_diff , home_spread_cover, qb_backup_home , avg_diff_from_spread_capped_diff, prime_time, temp_cat, distance_bucket)
  glm.fit <- glm(home_spread_cover~avg_qb_hits_differential_diff+avg_turnover_differential_diff + qb_backup_home +avg_diff_from_spread_capped_diff+temp_cat+distance_bucket+prime_time, data=train, family=binomial)
  glm.probs<-predict(glm.fit, test, type="response")
  test$probs <- glm.probs
  test$pred <- ifelse(glm.probs > 0.5, 1, 0)
  test$acc <- ifelse(test$pred == test$home_spread_cover, 1, 0)
  accuracy <- mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
  test_df<-rbind(test_df, test)
}
summary(accuracy_vector)
logistic_regression_acc_vector<-accuracy_vector
