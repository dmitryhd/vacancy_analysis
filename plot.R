file_name = read.table("data/plot_name.txt", quote="\"", stringsAsFactors=FALSE, sep=";")[,1]
title <-read.table("data/title.txt", quote="\"", stringsAsFactors=FALSE, sep=";")[,1]
pvac <- read.table("data/pvac.csv", header=TRUE, quote="\"", stringsAsFactors=FALSE)
pvac_labels <- read.table("data/pvac_labels.txt", quote="\"", stringsAsFactors=FALSE)
png(file_name, width = 1200, height = 800)
par(mar=c(4, 20, 2, 0.5))
boxplot(pvac, xaxt='n', las = 2, names=pvac_labels, ylim=c(20000, 200000), horizontal=T, col=rainbow(length(pvac)), main=title, xlab='Руб.')
abline(v = seq(10000, 300000, 10000), lty=1.5, lwd=0.5, col=336)
axis(side = 1, at = seq(10000, 300000, 10000))
dev.off()

