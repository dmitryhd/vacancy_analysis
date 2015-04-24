# main analysis module

library(bit)
library(cluster)

setwd('repos/vacancy_analysis/analysis_r/')

not.skill.vars <- c('max_sal', 'min_sal', 'max_exp', 'min_exp')

show.short <- function(set) {
    str(set, list.len=120)
}

load.dataset <- function() {
    # load vacancies csv file
    vacan <- read.csv("~/repos/vacancy_analysis/analysis_r/vacan_exp.csv", sep=";", stringsAsFactors=FALSE)
    vacan$X <- NULL

    for (field in not.skill.vars) {
        vacan[[field]] <- suppressWarnings(as.numeric(vacan[[field]]))
    }
    tmp <- vacan[!names(vacan) %in% not.skill.vars ]
    vacan <- vacan[rowSums(tmp) != 0,]
    vacan$min_exp[is.na(vacan$min_exp)] <- 0
    vacan$max_exp[is.na(vacan$max_exp)] <- 0
    vacan
}

calculate.mean.salary <- function(set) {
    set$min_sal[is.na(set$min_sal)] <- set$max_sal[is.na(set$min_sal)]
    set$max_sal[is.na(set$max_sal)] <- set$min_sal[is.na(set$max_sal)]
    set$mean_sal <- set$min_sal + (set$max_sal - set$min_sal)/2
    set
}

jaccard.metric <- function(a, b) {
    x <- sum(a | b)
    if (x == 0) {return(1)}
    dist <- 1 - sum(a & b) / x
    dist
}

dissimilarity.martix <- function(proc.vacan, metric) {
    len <- dim(proc.vacan)[1]
    bitmap <- list()
    for (i in 1:len) {
        bitmap[[i]] <- as.bit(as.integer(proc.vacan[i,]))
    }
    mat <- matrix(, nrow = len, ncol = len)
    for(column in 1:len){
        mat[, column] <- rep(NA, len)
    }
    for(row in 1:len) {
        for(col in row:len) {
            mat[row, col] <- metric(bitmap[[col]], bitmap[[row]])
        }
        cat("\r", 'calc row:', row)
    }
    for(row in 1:len) {
        for(col in 1:len-row) {
            if(col == 0) {next}
            mat[col, row] <- mat[row, col]
        }
        cat("\r", 'fill row:', row)
    }
    mat[is.na(mat)] <- 1
    for (i in 1:len) {
        mat[i, i] <- 0
    }
    mat
}

get.vector <- function(x) {
    y <- x
    y$max_sal <- NULL
    y$min_sal <- NULL
    y$min_exp <- NULL
    y$max_exp <- NULL
    y$clust <- NULL
    y$mean_sal <- NULL
    y$category <- NULL
    y
}

# PREPARE DATA
vacan <- load.dataset()
vacan.strip <- get.vector(vacan)

MAX.row <- 2000
cluster.number <- 5
train <- vacan_strip[1:MAX.row,]
train.full <- vacan[1:MAX.row,]
diss.mat <- get_dissimilarity_martix(train, jaccard.metric)

# CLUSTERIZATION
pamx <- pam(diss_mat, k=cluster.number, diss=TRUE)
train.full$clustering <- pamx$clustering

# Prepare data for inside cluster modelling

prepare.for.modelling <- function(train.full, cluster.number) {
    cl <- train.full[train.full$clustering == cluster.number,]
    cl <- calculate.mean.salary(cl)
    cl$R <- NULL
    cl$max_sal <- NULL
    cl$min_sal <- NULL
    cl$clustering <- NULL
    x<-names(cl)[colMeans(cl) >= 0.05]
    x <- x[!is.na(x)]
    cl.data <- cl[x]
    cl.data
}

linear.model <- function(x) {
    fit <- lm(mean_sal ~ . , data=x)
    pvals <- summary(fit)$coefficients[,4]
    important.features <- names(pvals[pvals < 0.05])
    vdata <- x[c(important.features[-1], 'mean_sal')]
    #fit <- lm(mean_sal ~ . , data=data.vdata)
    fit <- lm(mean_sal ~ . , data=vdata)
    fit$residuals
}

errs <- c()
for (cl.num in 1:cluster.number) {
    data <- prepare.for.modelling(train.full, cl.num)
    errs <- c(errs, linear.model(data))
    #boxplot(errors, horizontal = TRUE, main=paste('Residuals, cluster', cl.num))
}
boxplot(errs, horizontal = TRUE, main='Residuals')
abline(v=(seq(-200000,500000,10000)), col="lightgray", lty="dotted")

#abline(h=(seq(0,100,25)), col="lightgray", lty="dotted")

model <- lm(max_sal ~ min_exp + max_exp + python, data=cl1)
coef <- coefficients(model)
row <- cl1[1,]
row <- row[c('min_exp','max_exp','python')]
row <- c(1, as.numeric(row))
sal <- row %*% coef
abs(sal - cl1[1,]$max_sal)
