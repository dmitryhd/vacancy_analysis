source('analysis.R')
source('crossvalidation.R')

#err <- crossvalidation(vacan[1:4000,], perform.train, evaluate.test, 10, 1)

#boxplot(rs, horizontal = TRUE, main='Residuals k = 35')
#abline(v=(seq(-200000,500000,10000)), col="lightgray", lty="dotted")
#x<-ecdf(abs(rs))
#plot(x)
#abline(v=(seq(-200000,500000,10000)), col="lightgray", lty="dotted")
#abline(h=(seq(0,1,0.05)), col="lightgray", lty="dotted")

#x <- abs(rs)
#df <- data.frame(Residuadfl=x)
#df$mark <- rep('Cluster+LM', length(x))
#df$mark <- factor(df$mark)
#ggplot(df, aes(y=Residual, x=mark, fill=mark)) + geom_boxplot() + coord_flip()


print.cluster <- function(vacan, cl.name ) {
    vac <- calculate.mean.salary(vacan)
    vac <- calculate.mean.exp(vac)
    vac$R <- NULL
    vac$go <- NULL
    vac$mvc <- NULL
    vac$clust <- NULL
    clvac <- subset(vac, select=-c(mean_sal, mean_exp))
    vac.stat <- sort(colMeans(clvac), decreasing=TRUE)
    par(mar=c(8,6,4,2)+0.1,mgp=c(5,1,0))
    barplot(vac.stat[1:30], horiz=TRUE, las=1, main=paste('Skills in ', cl.name), xlab='Probability')
}

cl1 <- nnset[nnset$clust == 1,]
cl2 <- nnset[nnset$clust == 2,]
cl3 <- nnset[nnset$clust == 3,]
#cl3$mean_sal <-
mean_sals <- c(cl1$mean_sal, cl2$mean_sal, cl3$mean_sal)
marks <- c(
    rep('cluster #1', length(cl1$mean_sal)),
    rep('cluster #2', length(cl2$mean_sal)),
    rep('cluster #3', length(cl3$mean_sal)))
marks <- factor(marks)
salaries <- data.frame(salary = mean_sals, marks = marks)
ggplot(salaries, aes(y=salary, x=marks, fill=marks)) + geom_boxplot() + coord_flip() + scale_y_continuous(limits = c(50000, 1.1*10^5))
#saveRDS(diss.mat, 'diss.rds')
#readRDS()

plot.by.cl.num <- function(cl.num) {
    pamx <- pam(diss.mat, k=cl.num, diss=TRUE)
    nnset$clust <- pamx$clustering
    mean_sals <- c()
    marks <- c()
    for (i in 1:cl.num) {
        cln <- nnset[nnset$clust == i,]
        mean_sals <- c(mean_sals, cln$mean_sal)
        marks <- c(marks, rep(paste('cluster #', i, sep=''), length(cln$mean_sal)))
    }
    marks <- factor(marks)
    salaries <- data.frame(salary = mean_sals, marks = marks)
    png('plots/salary.distribution.png', units = "px", width=400, height=600)
    p <- ggplot(salaries, aes(y=salary, x=marks, fill=marks),) + ggtitle("Mounth salary distribution by cluster")
    p <- p + geom_boxplot() + coord_flip() + ylab("Mounth salary [$]") + xlab('')
    p <- p + scale_y_continuous(breaks = seq(800, 2500, 200),limits = c(800, 2500))
    p <- p + scale_fill_grey(start = 0, end = .9) + theme_bw()
    p
    dev.off()
    p
}
