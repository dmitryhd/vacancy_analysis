reload <- function () {
    library(ggplot2)
    source('analysis.R')
    source('crossvalidation.R')
    source('work.R')
    source('util.R')
}

show.short <- function(set) {
  str(set, list.len=120)
}


crossval.clust.lm <- function (train, k) {
    #params <- list(max.row=nrow(train), k=k, min.feature.occurences=0.00,
    #             max.feature.pval=0.05, cached.diss.mat=FALSE)
    #rs <- crossvalidation(params, train, train.kmean.lm, evaluate.kmean.lm, 10, 1)
    #rs
    params <- list(max.row=nrow(train), k=k, min.feature.occurences=0.00,
                   max.feature.pval=0.05, cached.diss.mat=FALSE) 
    rs2 <- crossvalidation(par, train, train.kmean.lm, evaluate.kmean.lm, 2, 1)
    rs2
}

crossval.clust.lm.all.k35. <- function (train) {
    params <- list(max.row=nrow(train), k=35, min.feature.occurences=0.0,
                   max.feature.pval=0.0, cached.diss.mat=FALSE)
    rs <- crossvalidation(params, train, train.kmean.lm, evaluate.test, 10, 1)
    rs
}

crossval.lm.only <- function (train) {
    params <- list(max.row=nrow(train), k=0, min.feature.occurences=0.05,
                   max.feature.pval=0.05, cached.diss.mat=FALSE)
    rs <- crossvalidation(params, train, train.lm.only, evaluate.test.lm.only, 10, 1)
    rs
}

session <- function() {
    vacan <- load.dataset()
    train <- vacan[1:2000,]
    #crossval.clust.lm(train, 5)
}

get.res <- function () {
    vacan <- load.dataset()
    train <- vacan[1:2000,]
    params <- list(max.row=nrow(train), k=5, min.feature.occurences=0.05,max.feature.pval=0.05, cached.diss.mat=FALSE)
    rs <- crossvalidation(params, train, train.kmean.lm, evaluate.test, 2, 1)
    rs
    df <- data.frame(residual=rs)
    df$mark <- rep('Cluster+LM', length(rs))
    df$mark <- factor(df$mark)
    params <- list(max.row=nrow(train), k=30, min.feature.occurences=0.05,max.feature.pval=0.05, cached.diss.mat=FALSE)
    rs <- crossvalidation(params, train, train.kmean.lm, evaluate.test, 2, 1)
    df$residual <- c(df$residual, rs)
    df$residual <- c(df$residual, rs)
}

run <- function () {
    rs1 <- crossvalidation(vacan[1:2000,], train.clust.lm.k1, evaluate.test, 2, 1);
    rs5 <- crossvalidation(vacan[1:2000,], train.clust.lm.k5, evaluate.test, 2, 1);
    rs15 <- crossvalidation(vacan[1:2000,], train.clust.lm.k15, evaluate.test, 2, 1);
    rs35 <- crossvalidation(vacan[1:2000,], train.clust.lm.k35, evaluate.test, 2, 1);
    rs1 <- rs1[!is.na(rs1)]
    rs5 <- rs5[!is.na(rs5)]
    rs15 <- rs15[!is.na(rs15)]
    rs35 <- rs35[!is.na(rs35)]
    residuals <- c(rs1, rs5, rs15, rs35)
    marks <- c(rep('clust+k1+lm', length(rs1)),
               rep('clust+k5+lm', length(rs5)),
               rep('clust+k15+lm', length(rs15)),
               rep('clust+k35+lm', length(rs35)))
    resid <- data.frame(err=residuals, mark=factor(marks))
    ggplot(resid, aes(y=err, x=mark, fill=mark)) + geom_boxplot() + coord_flip()
}

#train.res <- train.kmean.lm(params, vacan)  # this might save time
#residuals <- evaluate.train.kmean.lm(train.res[[2]])
