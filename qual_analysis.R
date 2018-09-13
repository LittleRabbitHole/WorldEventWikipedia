#contingency table
x = matrix(c(19, 37, 25, 34, 35, 
             52, 37, 33, 44, 48,
             33, 31, 22, 37, 45), ncol = 3)
chisq.test(x)

x = matrix(c(62, 114, 15, 20, 
             81, 147, 17, 31,
             68, 110, 17, 28), ncol = 3)
chisq.test(x)

x = matrix(c(52, 70, 89, 
             75, 88, 113,
             62, 68, 93), ncol = 3)
chisq.test(x)

######effort#########


######quality##########
qual_raw = read.csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Ang/rev_candidate_full_section.csv")
qual = qual_raw[c("external_links", "references", "size", "wiki_links","section_breadth", "section_depth", "section_num")]
pca_fit = prcomp(qual, center = T, scale = T)
#pca_fit$rotation
sum_pca_fit = summary(pca_fit)
pcs = data.frame(sum_pca_fit$x)
pca_var_df = cbind.data.frame(1:length(as.numeric(sum_pca_fit$importance[2,])),
                              as.numeric(sum_pca_fit$importance[2,]), 
                              as.numeric(sum_pca_fit$importance[3,]))

names(pca_var_df) = c("PC","Proportion Explained", "Cumulative Explained")
pca_var_df =  rbind(c(0,0,0), pca_var_df)
pca_var_df

library(ggplot2)

ggplot(pca_var_df, aes(x = PC, y = `Cumulative Explained`)) + 
  geom_point(size=3) +
  geom_line(size = 1.5) + 
  #geom_histogram(aes(y=`Proportion Explained`), stat="identity") + 
  xlim(0, 7) +
  ylim(0, 1)


o_qual = pcs$PC1
summary(o_qual)
hist(o_qual)
qual_raw$qual_score = o_qual

write.csv(qual_raw, file = "/Users/ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Ang/quality_data_score.csv", row.names=FALSE)


library(ggplot2)
qual_data = read.csv("/Users/angli/ANG/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Ang/quality_data.csv")
qual_data = read.csv("/Users/ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/Ang/quality_data.csv")
colnames(qual_data)

#community
summary(as.factor(qual_data$language))
qual_data$lan_cn = 0
qual_data$lan_cn[which(qual_data$language=='cn')] <- 1
qual_data$lan_en = 0
qual_data$lan_en[which(qual_data$language=='en')] <- 1
qual_data$lan_es = 0
qual_data$lan_es[which(qual_data$language=='es')] <- 1


summary(lm(formula = o1_qualscore ~ as.factor(lan_cn) + as.factor(lan_es), 
           data = qual_data))

summary(lm(formula = o2_qualscore ~ o1_qualscore + as.factor(lan_cn) + as.factor(lan_es), 
           data = qual_data))

summary(lm(formula = o3_qualscore ~ o2_qualscore + as.factor(lan_cn) + as.factor(lan_es), 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + as.factor(lan_cn) + as.factor(lan_es), 
           data = qual_data))
summary(lm(formula = o4_qualscore ~ o3_qualscore + as.factor(language), 
           data = qual_data))

ggplot(qual_data, aes(x=o4_qualscore, fill=as.factor(lan_en))) + geom_density(alpha=.3)



#topic
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

#location
qual_data$loc_Chinese = 0
qual_data$loc_Chinese[which(qual_data$location=="Chinese")] <- 1
qual_data$loc_English = 0
qual_data$loc_English[which(qual_data$location=="English")] <- 1
qual_data$loc_EnglishPlus = 0
qual_data$loc_EnglishPlus[which(qual_data$location=="English+")] <- 1
qual_data$loc_Spanish = 0
qual_data$loc_Spanish[which(qual_data$location=="Spanish")] <- 1



#size over location
hist(qual_data$o3_qualscore)

summary(lm(formula = qual_data$o1_qualscore ~ loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = qual_data$o2_qualscore ~ o1_qualscore + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = o3_qualscore ~ o2_qualscore + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + loc_Chinese + loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))


summary(lm(formula = o4_qualscore ~ loc_English + loc_EnglishPlus + loc_Spanish, 
           data = qual_data))

t.test( o4_qualscore~as.factor(loc_English), data = qual_data)
ggplot(qual_data, aes(x=o4_qualscore, fill=as.factor(loc_English))) + geom_density(alpha=.3)


summary(lm(formula = o1_qualscore ~ topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = o2_qualscore ~ o1_qualscore + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = o3_qualscore ~ o2_qualscore + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + topic_mandisaster + topic_naturaldisaster + topic_science, 
           data = qual_data))

###
summary(lm(formula = o1_qualscore ~ as.factor(year), 
           data = qual_data))

summary(lm(formula = o2_qualscore ~ o1_qualscore + as.factor(year), 
           data = qual_data))

summary(lm(formula = o3_qualscore ~ o2_qualscore + as.factor(year), 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + as.factor(year), 
           data = qual_data))


###
summary(lm(formula = o1_qualscore ~ as.factor(language), 
           data = qual_data))

summary(lm(formula = o2_qualscore ~ o1_qualscore + as.factor(language), 
           data = qual_data))

summary(lm(formula = o3_qualscore ~ o2_qualscore + as.factor(language), 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + as.factor(language), 
           data = qual_data))


#across community over localtion
summary(lm(formula = o1_qualscore ~ as.factor(language)*as.factor(location), 
           data = qual_data))

summary(lm(formula = o2_qualscore ~ o1_qualscore + as.factor(language)*as.factor(location), 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore + as.factor(language)*as.factor(location), 
           data = qual_data))

## across topics
summary(lm(formula = o1_qualscore ~ as.factor(language)*as.factor(topic_simple), 
           data = qual_data))

summary(lm(formula = o4_qualscore ~ o3_qualscore+as.factor(language)*as.factor(topic_simple), 
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
