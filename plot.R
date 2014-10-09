file_name = 'plots/vacancy_summary.png'
label <-read.table("data/label.txt", quote="\"", stringsAsFactors=FALSE, sep=";")
pvac <- read.table("data/pvac.csv", header=TRUE, quote="\"", stringsAsFactors=FALSE)
pvac_labels <- read.table("data/pvac_labels.txt", quote="\"", stringsAsFactors=FALSE)
png(file_name, width = 1200, height = 800)
par(mar=c(4, 20, 2, 0.5))
boxplot(pvac, xaxt='n', las = 2, names=pvac_labels, ylim=c(20000, 200000), horizontal=T, col=rainbow(length(pvac)), main=label[,1], xlab='Руб.')
abline(v = seq(10000, 300000, 10000), lty=1.5, lwd=0.5, col=336)
axis(side = 1, at = seq(10000, 300000, 10000))
dev.off()

