M <- as.table(rbind(c(172,115,472,746,114,445), c(29084236,10126202,36385900,65570985,12605752,50669937)))
dimnames(M) <- list(community = c("EnglishWiki","Global"), 
                    language = c('Arabic','Chinese','English','Others','Spanish','US'))

M <- as.table(rbind(c(115,746,114,445), c(101.26202,655.70985,126.05752,506.69937)))
dimnames(M) <- list(community = c("EnglishWiki","Global"), 
                    language = c('Chinese','Others','Spanish','US'))


Xsq <- chisq.test(M)


setwd("~/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/finaldata")
data = read.csv("effort_dataset.csv")
colnames(data)

engdata = data[which(data$lang == "en"),]
write.csv(engdata, "eng_effort_dataset.csv")

nonengdata = data[which(data$lang != "en"),]
write.csv(nonengdata, "non_eng_effort_dataset.csv")

setwd("~/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEventsWikipedia/data/Ang/revise/finaldata/Ang")

data = read.csv("quality_dataset2.csv")
colnames(data)

engdata = data[which(data$lang == "en"),]
write.csv(engdata, "eng_quality_dataset.csv")
