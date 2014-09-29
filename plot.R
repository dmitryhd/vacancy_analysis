pvac <- read.csv("data/pvac.csv", sep=";", stringsAsFactors=FALSE)

datasets <- list(pvac[which(pvac$python==1),],
              pvac[which(pvac$c..==1),],
              pvac[which(pvac$java==1),],
              pvac[which(pvac$php==1),],
              pvac[which(pvac$perl==1),],
              pvac[which(pvac$ruby==1),],
              pvac[which(pvac$bash==1),],
              pvac[which(pvac$javascript==1),],
              pvac[which(pvac$X1c==1),],
              pvac[which(pvac$sap==1),]
              )

descriptions1 <- c('python','cpp','java','php','perl','ruby','bash','javascript','x1c','sap')

getdf <- function(datasets, descriptions, file_name) {
  max_size <- 0
  for (data in datasets) {
    max_size <- max(max_size, length(data$max_salary), length(data$min_salary))
  }
  names <- c()
  names_min <- c()
  names_max <- c()
  mns <- c()
  s_max <- list()
  s_min <- list()
  for (i in 1:length(datasets)) {
    data <- datasets[[i]]
    print(descriptions[i])
    pm1 <- as.numeric(data$max_salary)
    need_size <- maxsize - length(data$max_salary)
    new_max <- c(pm1, rep(NA, need_size))
    pm2 <- as.numeric(data$min_salary)
    need_size <- maxsize - length(data$min_salary)
    new_min <- c(pm2, rep(NA, need_size))
    mn_max <-mean(pm1, na.rm=T)
    mn_min <-mean(pm2, na.rm=T)
    mn <- mean(c(pm1, pm2), na.rm=T)
    max_name <- paste(descriptions[i],'_max',sep = "")
    min_name <- paste(descriptions[i],'_min',sep = "")
    print(list(mn, max_name, min_name, pm1, pm2))
    mns <- c(mns, mn)
    names_min <- c(names_min, min_name)
    names_max <- c(names_max, max_name)
    names <- c(names, descriptions[i])
    s_max[[i]] <- new_max
    s_min[[i]] <- new_min
  }  
  df <- data.frame(rep(NA, max_size))
  prepared_data <- data.frame(mns, names_min, names_max, names, stringsAsFactors=FALSE)
  plot_labels <- c()
  for (i in with(prepared_data, order(mns))) {
    print(prepared_data[i,2])
    df[prepared_data[i,3]] <- s_max[[i]]
    df[prepared_data[i,2]] <- s_min[[i]]
    plot_labels <- c(plot_labels, paste(prepared_data[i,4], ' мин. [Сердн.=', format(round(prepared_data[i,1], -3), scientific=F), '] ', 'Вакансий:', length(datasets[[i]]$max_salary), sep=''))
    plot_labels <- c(plot_labels, paste(prepared_data[i,4], ' мaкс. [Сердн.=', format(round(prepared_data[i,1], -3), scientific=F), '] ', 'Вакансий:', length(datasets[[i]]$max_salary), sep=''))
  }
  df$rep.NA..max_size. <- NULL

  png(file_name, width = 1200, height = 800)
  par(mar=c(4, 20, 2, 0.5))
  boxplot(df, xaxt='n', las = 2, ylim=c(20000, 200000), names=plot_labels, horizontal=T, col=rainbow(length(df)), main='Зарплата программистов (hh.ru 29.09.2014, Khodakov)', xlab='Руб.')
  abline(v = seq(10000, 300000, 10000), lty=1.5, lwd=0.5, col=336)
  axis(side = 1, at = seq(10000, 300000, 10000))
  dev.off()
  return(df)
}
getdf(datasets, descriptions1, 'plots/vacancy_summary.png')
#df <- getdf(datasets, descriptions1)