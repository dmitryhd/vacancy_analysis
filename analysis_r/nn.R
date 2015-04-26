library("neuralnet")
cl2 <- nnset[nnset$clust == 2,]
cl2 <- calculate.mean.salary(cl2)
cl2 <- calculate.mean.exp(cl2)
cl2$R <- NULL
x<-sort(colMeans(cl2), decreasing=TRUE)
import<-names(x[1:(length(x)*0.4)])
nntrain <- cl2[1:300,]
nntrain <- subset(nntrain, select=import)
nntest <- cl2[300:nrow(cl2),]
nntest <- subset(nntest, select=import)
actual <- nntest$mean_sal 
nntest <- subset(nntest, select=-c(mean_sal))
results <- data.frame(actual = actual, prediction = creditnet.results$net.result)
x <- names(nntrain)
x<-x[x!='mean_sal']
formula <- as.formula(paste("mean_sal ~ ", paste(x, collapse = '+')))

net <- neuralnet(formula, nntrain, hidden = 4, lifesign = "minimal", linear.output = FALSE, threshold = 0.1)
net <- neuralnet(formula, nntrain, hidden = 10, lifesign = "minimal", linear.output = TRUE, threshold = 0.1, rep=10)
plot(net, rep = "best")
net.results <- compute(net, nntest)
