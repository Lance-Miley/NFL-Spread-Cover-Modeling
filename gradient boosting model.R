library(dplyr)
library(gbm)
modeling_data <- read.csv("modeling_dataset.csv")
modeling_data$home_spread_cover<-ifelse(modeling_data$home_spread_cover=="True", 1, 0)
modeling_data$qb_backup_home <- ifelse(modeling_data$qb_backup_home=="", "N", modeling_data$qb_backup_home)
modeling_data$qb_backup_away <- ifelse(modeling_data$qb_backup_away=="", "N", modeling_data$qb_backup_away)
wks_2_18 <- modeling_data %>%
  filter(week <=18, week >1)

### Gradient Boosting Machines ###

wks_2_18_gbm<- wks_2_18 %>% select('home_spread_cover', 'year', 'avg_point_differential_diff','avg_yard_differential_diff','avg_turnover_differential_diff','weighted_dvoa_diff','total_dvoa_rank_diff','avg_diff_from_spread_capped_diff','spread_line',
                                   "avg_qb_hits_differential_diff", "avg_two_min_differential_diff", 'prime_time', 'temp_cat', 'distance_bucket', 'qb_backup_home', 'qb_backup_away')
wks_2_18_gbm<-na.omit(wks_2_18_gbm)

wks_2_18_gbm$prime_time <- as.character(wks_2_18_gbm$prime_time)
wks_2_18_gbm$prime_time <- as.factor(wks_2_18_gbm$prime_time)

wks_2_18_gbm$temp_cat <- as.character(wks_2_18_gbm$temp_cat )
wks_2_18_gbm$temp_cat <- as.factor(wks_2_18_gbm$temp_cat )

wks_2_18_gbm$distance_bucket <- as.character(wks_2_18_gbm$distance_bucket )
wks_2_18_gbm$distance_bucket <- as.factor(wks_2_18_gbm$distance_bucket )

wks_2_18_gbm$qb_backup_home <- as.character(wks_2_18_gbm$qb_backup_home )
wks_2_18_gbm$qb_backup_home <- as.factor(wks_2_18_gbm$qb_backup_home )

wks_2_18_gbm$qb_backup_away <- as.character(wks_2_18_gbm$qb_backup_away )
wks_2_18_gbm$qb_backup_away <- as.factor(wks_2_18_gbm$qb_backup_away )


hyper_grid <- expand.grid(
  shrinkage = c(0.001, 0.005, 0.01,0.05, 0.1),
  interaction.depth=c(1,2,3),
  n.trees=c(100, 500, 1000),
  accuracy=0
)

test_df <- data.frame(matrix(nrow=0, ncol=3))
colnames(test_df)<-c('home_spread_cover', 'pred', 'acc')#c('week', 'avg_qb_hits_differential_diff', 'avg_turnover_differential_diff' , 'home_spread_cover', 'qb_backup_home' , 'avg_diff_from_spread_capped_diff', 'prime_time', 'temp_cat', 'distance_bucket', 'pred', 'acc')

for (i in 1:nrow(hyper_grid)){
  test_df <- data.frame(matrix(nrow=0, ncol=3))
  colnames(test_df)<-c('home_spread_cover', 'pred', 'acc')
  for (yr in unique(modeling_data$year)) {
    train <- wks_2_18_gbm[wks_2_18_gbm$year != yr, ]
    test<-wks_2_18_gbm[wks_2_18_gbm$year == yr, ]
    gbm.fit<-gbm(home_spread_cover~avg_turnover_differential_diff+avg_diff_from_spread_capped_diff+
                   avg_qb_hits_differential_diff+prime_time+temp_cat+distance_bucket+qb_backup_home,
                 data=train, distribution = "bernoulli", cv.folds=10, shrinkage=hyper_grid$shrinkage[i]
                 , n.trees = hyper_grid$n.trees[i], interaction.depth=hyper_grid$interaction.depth[i])
    gbm.pred<-predict.gbm(object = gbm.fit,
                          newdata = test,
                          n.trees=hyper_grid$n.trees[i],
                          type="response")
    
    temp<-test%>%select(home_spread_cover, year)
    temp$pred<-ifelse(gbm.pred>0.5, 1, 0)
    temp$acc<-ifelse(temp$pred == temp$home_spread_cover,1,0)
    test_df<-rbind(test_df, temp)
  }
  hyper_grid$accuracy[i]<-mean(test_df$acc)
  print(paste("shrinkage:", hyper_grid$shrinkage[i], ", Number of trees:",hyper_grid$n.trees[i], "Tree Depth:", hyper_grid$interaction.depth[i], ", Mean: ", mean(test_df$acc) ))
}
hyper_grid %>%
  arrange(desc(accuracy))


test_df <- data.frame(matrix(nrow=0, ncol=3))
colnames(test_df)<-c('home_spread_cover', 'pred', 'acc')

for (i in 1:nrow(hyper_grid)){
  test_df <- data.frame(matrix(nrow=0, ncol=3))
  colnames(test_df)<-c('home_spread_cover', 'pred', 'acc')
  for (yr in unique(modeling_data$year)) {
    train <- wks_2_18_gbm[wks_2_18_gbm$year != yr, ]
    test<-wks_2_18_gbm[wks_2_18_gbm$year == yr, ]
    gbm.fit<-gbm(home_spread_cover~avg_point_differential_diff+avg_yard_differential_diff+avg_turnover_differential_diff+weighted_dvoa_diff+total_dvoa_rank_diff+avg_diff_from_spread_capped_diff+spread_line+
                   +avg_qb_hits_differential_diff+avg_two_min_differential_diff+prime_time+temp_cat+distance_bucket+qb_backup_home+qb_backup_away,
                 data=train, distribution = "bernoulli", cv.folds=10, shrinkage=hyper_grid$shrinkage[i]
                 , n.trees = hyper_grid$n.trees[i], interaction.depth=hyper_grid$interaction.depth[i])
    gbm.pred<-predict.gbm(object = gbm.fit,
                          newdata = test,
                          n.trees=hyper_grid$n.trees[i],
                          type="response")
    
    temp<-test%>%select(home_spread_cover, year)
    temp$pred<-ifelse(gbm.pred>0.5, 1, 0)
    temp$acc<-ifelse(temp$pred == temp$home_spread_cover,1,0)
    test_df<-rbind(test_df, temp)
  }
  hyper_grid$accuracy[i]<-mean(test_df$acc)
  print(paste("shrinkage:", hyper_grid$shrinkage[i], ", Number of trees:",hyper_grid$n.trees[i], "Tree Depth:", hyper_grid$interaction.depth[i], ", Mean: ", mean(test_df$acc) ))
}
hyper_grid %>%
  arrange(desc(accuracy)) #Best Model's Parameters-- Shrinkage: 0.005; Depth: 1; number of trees: 1000

#Fit the best GBM 

accuracy_vector<-c()
for (yr in unique(modeling_data$year)) {
  train <- wks_2_18_gbm[wks_2_18_gbm$year != yr, ]
  test<-wks_2_18_gbm[wks_2_18_gbm$year == yr, ]
  gbm.fit<-gbm(home_spread_cover~avg_point_differential_diff+avg_yard_differential_diff+avg_turnover_differential_diff+weighted_dvoa_diff+total_dvoa_rank_diff+avg_diff_from_spread_capped_diff+spread_line+
                 +avg_qb_hits_differential_diff+avg_two_min_differential_diff+prime_time+temp_cat+distance_bucket+qb_backup_home+qb_backup_away,
               data=train, distribution = "bernoulli", cv.folds=10, shrinkage=0.005
               , n.trees = 1000, interaction.depth=1)
  gbm.pred<-predict.gbm(object = gbm.fit,
                        newdata = test,
                        n.trees=1000,
                        type="response")
  
  temp<-test%>%select(home_spread_cover, year)
  temp$pred<-ifelse(gbm.pred>0.5, 1, 0)
  temp$acc<-ifelse(temp$pred == temp$home_spread_cover,1,0)
  accuracy<-mean(na.omit(temp$acc))
  accuracy_vector <- c(accuracy_vector, accuracy)
}
summary(accuracy_vector)
gbm_acc_vector<-accuracy_vector

