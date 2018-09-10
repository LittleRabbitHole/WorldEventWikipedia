qual_data = read.csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Ang/quality_data.csv")
colnames(qual_data)

summary(as.factor(qual_data$topic_simple))
#-1   0   3   6 
#211 371  49  79 
qual_data$topic_mandisaster = 0
qual_data$topic_mandisaster[which(qual_data$topic_simple==0)] <- 1
qual_data$topic_naturaldisaster = 0
qual_data$topic_naturaldisaster[which(qual_data$topic_simple==3)] <- 1
qual_data$topic_science = 0
qual_data$topic_science[which(qual_data$topic_simple==6)] <- 1

summary(as.factor(qual_data$location))
#Chinese  English English+   Others  Spanish 
#55      131       87      397       40 

qual_data$loc_Chinese = 0
qual_data$loc_Chinese[which(qual_data$location=="Chinese")] <- 1
qual_data$loc_English = 0
qual_data$loc_English[which(qual_data$location=="English")] <- 1
qual_data$loc_EnglishPlus = 0
qual_data$loc_EnglishPlus[which(qual_data$location=="English+")] <- 1
qual_data$loc_Spanish = 0
qual_data$loc_Spanish[which(qual_data$location=="Spanish")] <- 1

#size over location

summary(lm(formula = log(o1_size+0.01) ~ loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = log(o2_size+0.01) ~ log(o1_size+0.01) + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = log(o3_size+0.01) ~ log(o2_size+0.01) + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = log(o4_size+0.01) ~ log(o3_size+0.01) + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))


# size of the topics


summary(lm(formula = log(o1_size+0.01) ~ topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = log(o2_size+0.01) ~ log(o1_size+0.01) + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = log(o3_size+0.01) ~ log(o2_size+0.01) + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = log(o4_size+0.01) ~ log(o3_size+0.01) + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))


# size over communities

summary(lm(formula = log(o1_size+0.01) ~ as.factor(language), 
           data = qual_data))

summary(lm(formula = log(o2_size+0.01) ~ log(o1_size+0.01) + as.factor(language), 
           data = qual_data))

summary(lm(formula = log(o3_size+0.01) ~ log(o2_size+0.01) + as.factor(language), 
           data = qual_data))

summary(lm(formula = log(o4_size+0.01) ~ log(o3_size+0.01) + as.factor(language), 
           data = qual_data))
#the most resent, three langage communities have article sizes are comparible



#across community over localtion
summary(lm(formula = log(o1_size+0.01) ~ as.factor(language)*as.factor(location), 
           data = qual_data))

summary(lm(formula = log(o2_size+0.01) ~ log(o1_size+0.01) + as.factor(language)*as.factor(location), 
           data = qual_data))

summary(lm(formula = log(o4_size+0.01) ~ log(o3_size+0.01) + as.factor(language)*as.factor(location), 
           data = qual_data))


## across topics
summary(lm(formula = log(o1_size+0.01) ~ as.factor(language)*as.factor(topic_simple), 
           data = qual_data))

summary(lm(formula = log(o2_size+0.01) ~ log(o1_size+0.01)+as.factor(language)*as.factor(topic_simple), 
           data = qual_data))

summary(lm(formula = log(o3_size+0.01) ~ log(o2_size+0.01)+as.factor(language)*as.factor(topic_simple), 
           data = qual_data))

summary(lm(formula = log(o4_size+0.01) ~ log(o3_size+0.01)+as.factor(language)*as.factor(topic_simple), 
           data = qual_data))
