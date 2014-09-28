
# Any programmer 
png(filename="plots/min_max_salary.png")
par(mfrow=c(2,1))
hist(as.numeric(pvac$min_salary), breaks=50, col="lightblue", xlim=c(40000, 300000), xlab='Minimum salary (RUB)', main='Minimum salary of programmer (any language) (28.09.2014 hh.ru)')
hist(as.numeric(pvac$max_salary), breaks=80, col="chocolate1", xlim=c(40000, 300000), xlab='Maximum salary (RUB)', main='Maximum salary of programmer (any language) (28.09.2014 hh.ru)')
dev.off()

png(filename="plots/min_max_salary_boxplot.png")
par(mfrow=c(2,1))
boxplot(as.numeric(pvac$min_salary), ylim=c(0,200000),col="lightblue", horizontal=TRUE, main='Minimum salary of programmer (any language) (28.09.2014 hh.ru)')
boxplot(as.numeric(pvac$max_salary), ylim=c(0,200000),col="chocolate1", horizontal=TRUE, main='Maximum salary of programmer (any language) (28.09.2014 hh.ru)')
dev.off()

datasets <- list(pvac[which(pvac$python==1),],
              pvac[which(pvac$c..==1),],
              pvac[which(pvac$java==1),],
              pvac[which(pvac$php==1),],
              pvac[which(pvac$perl==1),],
              pvac[which(pvac$ruby==1),],
              pvac[which(pvac$bash==1),],
              pvac[which(pvac$javascript==1),],
              pvac[which(pvac$X1c==1),],
              pvac[which(pvac$sap==1),],
              pvac[which(pvac$matlab==1),],
              pvac[which(pvac$net==1),]
              )

descriptions <- c(paste('python (', length(datasets[[1]]$max_salary), ' vacancies)'),
                  paste('c++ (', length(datasets[[2]]$max_salary), ' vacancies)'),
                  paste('java (', length(datasets[[3]]$max_salary), ' vacancies)'),
                  paste('php (', length(datasets[[4]]$max_salary), ' vacancies)'),
                  paste('perl (', length(datasets[[5]]$max_salary), ' vacancies)'),
                  paste('ruby (', length(datasets[[6]]$max_salary), ' vacancies)'),
                  paste('bash (', length(datasets[[7]]$max_salary), ' vacancies)'),
                  paste('javascript (', length(datasets[[8]]$max_salary), ' vacancies)'),
                  paste('1c (', length(datasets[[9]]$max_salary), ' vacancies)'),
                  paste('sap (', length(datasets[[10]]$max_salary), ' vacancies)'),
                  paste('matlab (', length(datasets[[11]]$max_salary), ' vacancies)'),
                  paste('net (', length(datasets[[12]]$max_salary), ' vacancies)')
                  )
filenames <- c('plots/python.png','plots/cpp.png','plots/java.png','plots/php.png','plots/perl.png','plots/ruby.png','plots/bash.png','plots/js.png','plots/1c.png','plots/sap.png','plots/matlab.png', 'plots/net.png')

salary_boxplots <- function(data, desc, file_name) {
  png(filename=file_name)
  title_min <- paste('Minimum salary of programmer ', desc, ' (28.09.2014 hh.ru)')
  title_max <- paste('Maximum salary of programmer ', desc, ' (28.09.2014 hh.ru)')
  par(mfrow=c(2,1))
  boxplot(as.numeric(data$min_salary), ylim=c(0,200000),col="lightblue", horizontal=TRUE, main=title_min, xlab='Salary (Ru)')
  boxplot(as.numeric(data$max_salary), ylim=c(0,200000),col="chocolate1", horizontal=TRUE, main=title_max, xlab='Salary (Ru)')
  dev.off()
}

for (i in 1:11) {
  salary_boxplots(datasets[[i]], descriptions[i], filenames[i])
}