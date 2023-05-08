library(ggplot2)

df_boxplot <- data.frame(logistic_regression_acc_vector, 'logistic')%>% rename('accuracy' = 1,'model' = 2) %>%
  rbind(data.frame(rf_acc_vector, 'random forest') %>% rename('accuracy' = 1,'model' = 2)) %>%
  rbind(data.frame(ridge_acc_vector, 'ridge') %>% rename('accuracy' = 1,'model' = 2)) %>%
  rbind(data.frame(gam_acc_vector, 'gam') %>% rename('accuracy' = 1,'model' = 2)) %>%
  rbind(data.frame(gbm_acc_vector, 'gbm') %>% rename('accuracy' = 1,'model' = 2))

ggplot(data = df_boxplot, mapping=aes(x=model, y = accuracy)) +
  geom_boxplot(size = 0.4) +
  ggtitle("Mean Accuracy by Season Boxplots")+
  theme(plot.title = element_text(hjust = 0.5, size = 8),
        axis.title.x = element_text(size = 6),
        axis.text.x=element_text(size=6),
        axis.text.y=element_text(size=6),
        axis.title.y=element_text(size=7),
        legend.text=element_text(size=4),
        legend.title=element_text(size=0.4))+
  stat_summary(fun=mean, geom="point",aes(shape="mean"),  size=3, color="red")+
  scale_shape_manual("", values=c("mean"="x"))
ggsave(paste(getwd(), "/validation/Model Performance Boxplots.jpeg", sep=""), width=3.5, height=2.5)



accuracy_vectors <- c('logistic_regression_acc_vector', 'ridge_acc_vector', 'rf_acc_vector', 'gam_acc_vector','gbm_acc_vector')
models<-c('Logistic Regression', 'Ridge', 'Random Forest', 'GAM', 'GBM')

for(i in 1:length(accuracy_vectors)) {
  years = unique(wks_2_18$year) 
  df=data.frame(get(accuracy_vectors[i]), years) %>% rename('accuracy' = 1,'Season' = 2)
  
  plot <- ggplot(data =df,aes(Season, accuracy)) +
    geom_point(size = 0.8)+
    geom_smooth(method=lm, se=FALSE, aes(colour="linear trend"), size = 0.7)+
    scale_colour_manual(name="", values="blue")+
    ggtitle(paste("Mean Accuracy by Season:", models[i]))+
    theme(plot.title = element_text(hjust = 0.5, size=8),
          axis.title.x=element_text(size=7),
          axis.text.x=element_text(size=6),
          axis.text.y=element_text(size=6),
          axis.title.y=element_text(size=7),
          legend.text=element_text(size=5),
          legend.title=element_text(size=0.5))+
    xlab("Season")+ ylab("Mean Accuracy")
  
  print(plot)
  ggsave(paste(getwd(), "/validation/", "Mean Accuracy by Season-- ", models[i], ".jpeg", sep=""), height=2.5, width=3.5)
}

