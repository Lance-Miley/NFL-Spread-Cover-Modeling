library(dplyr)
library(randomForest)
modeling_data <- read.csv("modeling_dataset.csv")
modeling_data$home_spread_cover<-ifelse(modeling_data$home_spread_cover=="True", 1, 0)
modeling_data$qb_backup_home <- ifelse(modeling_data$qb_backup_home=="", "N", modeling_data$qb_backup_home)
modeling_data$qb_backup_away <- ifelse(modeling_data$qb_backup_away=="", "N", modeling_data$qb_backup_away)
wks_2_18 <- modeling_data %>%
  filter(week <=18, week >1)

### Random Forest ###

wks_2_18_rf<- wks_2_18 %>% select('home_spread_cover','year', 'avg_point_differential_diff','avg_yard_differential_diff','avg_turnover_differential_diff','weighted_dvoa_diff','total_dvoa_rank_diff','avg_diff_from_spread_capped_diff','spread_line',
                                  "avg_qb_hits_differential_diff", "avg_two_min_differential_diff", 'prime_time', 'temp_cat', 'distance_bucket', 'qb_backup_home', 'qb_backup_away')
wks_2_18_rf<-na.omit(wks_2_18_rf)
wks_2_18_rf$home_spread_cover <- as.character(wks_2_18_rf$home_spread_cover)
wks_2_18_rf$home_spread_cover <- as.factor(wks_2_18_rf$home_spread_cover)
accuracy_vector<-c()

for (yr in unique(modeling_data$year)) {
  train <- wks_2_18_rf[wks_2_18_rf$year != yr, ]
  test<-wks_2_18_rf[wks_2_18_rf$year == yr, ]
  
  rf.football <- randomForest(home_spread_cover ~ 
                                avg_point_differential_diff+avg_yard_differential_diff+avg_turnover_differential_diff+weighted_dvoa_diff+total_dvoa_rank_diff+avg_diff_from_spread_capped_diff+spread_line+
                                +avg_qb_hits_differential_diff+avg_two_min_differential_diff+prime_time+temp_cat+distance_bucket+qb_backup_home+qb_backup_away
                              , data = train, mtry = 4, importance = TRUE, ntree=2500, proximity=TRUE)
  test$pred<-predict(rf.football, newdata=test)
  test$acc <- ifelse(test$pred == test$home_spread_cover, 1,0)
  accuracy<-mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector)
rf_acc_vector<-accuracy_vector


accuracy_vector<-c()
for (yr in unique(modeling_data$year)) {
  train <- wks_2_18_rf[wks_2_18_rf$year != yr, ]
  test<-wks_2_18_rf[wks_2_18_rf$year == yr, ]
  
  rf.football <- randomForest(home_spread_cover ~ 
                                avg_turnover_differential_diff+avg_diff_from_spread_capped_diff+
                                avg_qb_hits_differential_diff+prime_time+temp_cat+distance_bucket+qb_backup_home
                              , data = train, mtry = 3, importance = TRUE, ntree=2500, proximity=TRUE)
  test$pred<-predict(rf.football, newdata=test)
  test$acc <- ifelse(test$pred == test$home_spread_cover, 1,0)
  accuracy<-mean(na.omit(test$acc))
  print(paste(yr, ": ", accuracy))
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector)
