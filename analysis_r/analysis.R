# Vacancy analysis main module. 
# Performs kmean clustering of texts with jaccard distance
# Then do linear model for significant features in every cluster

# Authod: Dmitriy Khodakov <dmitryhd@gmail.com>

library(bit)
library(cluster)

not.skill.vars <- c('max_sal', 'min_sal', 'max_exp', 'min_exp')
added.vars <- c('clustering', 'mean_sal', 'category')

show.short <- function(set) {
  str(set, list.len=120)
}

load.dataset <- function() {
  # Load vacancies csv file. Return dataset
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

jaccard.metric <- function(a, b) {
  # Calculate distance for 2 binary vectors of words.
  # Return number in 0, 1 interval, means that a == b
  x <- sum(a | b)
  if (x == 0) {return(1)}
  dist <- 1 - sum(a & b) / x
  dist
}

dissimilarity.martix <- function(proc.vacan, metric) {
  # Return matrix of dissimilarity, using metric
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
  cat("\r", '                               ') # clear srting
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

calculate.mean.salary <- function(set) {
  # Return set with new mean_sal field
  set$min_sal[is.na(set$min_sal)] <- set$max_sal[is.na(set$min_sal)]
  set$max_sal[is.na(set$max_sal)] <- set$min_sal[is.na(set$max_sal)]
  set$mean_sal <- set$min_sal + (set$max_sal - set$min_sal)/2
  set
}

prepare.for.modelling <- function(params, train.full, cluster.number) {
  # Prepare data for inside cluster modelling
  # return prapared, cleared data for given current cluster number
  cl <- train.full[train.full$clustering == cluster.number,]
  cl <- calculate.mean.salary(cl)
  cl$R <- NULL
  cl$max_sal <- NULL
  cl$min_sal <- NULL
  cl$clustering <- NULL
  x<-names(cl)[colMeans(cl) >= params$min.feature.occurences]
  x <- x[!is.na(x)]
  cl.data <- cl[x]
  cl.data
}

linear.model <- function(params, x) {
  # fit linear model - return model
  fit <- lm(mean_sal ~ . , data=x)
  pvals <- summary(fit)$coefficients[,4]
  important.features <- names(pvals[pvals < params$max.feature.pval])
  print(c(important.features[-1], 'mean_sal'))
  vdata <- x[c(important.features[-1], 'mean_sal')]
  #vdata <-x
  fit <- lm(mean_sal ~ . , data=vdata)
  fit
}

train.lm <- function(params, train.full) {    
  # Return list of models by cluster number
  models <- list()
  for (cl.num in 1:params$k) {
    data <- prepare.for.modelling(params, train.full, cl.num)
    models[[cl.num]] <- linear.model(params, data)
  }
  models
}

clear.data <- function(x) {
  # Delete not significant fields
  for (field in c(added.vars, not.skill.vars)) {
    x[field] <- NULL
  }
  x$R <- NULL
  return(x)
}

get.diss.matrix <- function(vacan, max.row) {
  # return diss matrix
  vacan.strip <- clear.data(vacan)
  train <- vacan.strip[1:max.row,]
  mat <- dissimilarity.martix(train, jaccard.metric)
  return (mat)
}

train.kmean.lm <- function(params, vacan) {
  # Perform train
  # With given data 
  # 1. clusterize with kmeans and jaccard metric
  # 2. perform linear model on data
  # Return [cluster, models]
  train.full <- vacan[1:params$max.row,]
  if (params$cached.diss.mat == FALSE) {
    diss.mat <- get.diss.matrix(train.full, params$max.row)
  }
  else {
    diss.mat <- params$diss.mat
  }
  cat('===== diss matrix got\n')
  # CLUSTERIZATION
  pamx <- pam(diss.mat, k=params$k, diss=TRUE)
  train.full$clustering <- pamx$clustering    
  cat('===== clusterization done\n')
  # LM
  models <- train.lm(params, train.full)
  cat('===== lm done\n')
  return (list(cluster=pamx, models=models, train=train.full))
}

evaluate.train.kmean.lm <- function(lmodels) {
  # Evaluate residuals for train set
  cluster.number <- length(lmodels)
  residuals <- c()
  for (cl.num in 1:cluster.number) {
    residuals <- c(residuals, lmodels[[cl.num]]$residuals)
  }
  return(residuals)
}
train.clust.lm.k1 <- function(train) {
  params <- list(max.row=nrow(train), k=1, min.feature.occurences=0.05,
                 max.feature.pval=0.05, cached.diss.mat=FALSE)
  train.res <- train.kmean.lm(params, train)
  train.res
}

train.clust.lm.k5 <- function(train) {
  params <- list(max.row=nrow(train), k=5, min.feature.occurences=0.05,
                 max.feature.pval=0.05, cached.diss.mat=FALSE)
  train.res <- train.kmean.lm(params, train)
  train.res
}

train.clust.lm.k15 <- function(train) {
  params <- list(max.row=nrow(train), k=15, min.feature.occurences=0.05,
                 max.feature.pval=0.05, cached.diss.mat=FALSE)
  train.res <- train.kmean.lm(params, train)
  train.res
}

train.clust.lm.k35 <- function(train) {
  params <- list(max.row=nrow(train), k=35, min.feature.occurences=0.05,
                 max.feature.pval=0.05, cached.diss.mat=FALSE)
  train.res <- train.kmean.lm(params, train)
  train.res
}

get.nearest <- function(point, train) {
  min.dist <- 2
  nearest.index <- 0
  for (i in 1:length(train)) {
    dist <- jaccard.metric(point, train[[i]])
    if (dist < min.dist) {
      min.dist <- dist
      nearest.index <- i
    }
  }
  nearest.index
}

evaluate.test <- function(train.res, test) {
  # SET CLUSTERS to test
  pamx <- train.res$cluster
  models <- train.res$models
  train.bit <- list()
  cleared.train <- clear.data(train.res$train)
  for (i in 1:nrow(cleared.train)) {
    train.bit[[i]] <- as.bit(as.integer(cleared.train[i,]))
  }
  clusters <- train.res$train$clustering
  test.clusters <- c()
  for (i in 1:nrow(test)) {
    point <- as.bit(as.integer(clear.data(test[i,])))
    nearest.index <- get.nearest(point, train.bit)
    point.clust <- clusters[nearest.index]
    test.clusters <- c(test.clusters, point.clust)
  }
  test$clustering <- test.clusters
  test2 <- calculate.mean.salary(test)
  
  residuals <- c()
  # evaluate model errors
  for (i in 1:nrow(test2)) {
    cur.clust <- test2[i,][,"clustering"]
    coefs <- models[[cur.clust]]$coefficients
    if (length(coefs) > 1) {
      coefs <- coefs[names(coefs) != '(Intercept)']
      point <- test2[names(coefs)][i,]
      estimate <- sum(point * coefs) + models[[cur.clust]]$coefficients['(Intercept)']
    }
    if (length(coefs) == 1) {
      estimate <- models[[cur.clust]]$coefficients['(Intercept)']
    }
    res <- as.numeric(test2[i,]$mean_sal - estimate)
    residuals <- c(residuals, res)
  }
  residuals <- as.numeric(residuals)
  residuals
}

# LOAD DATA
vacan <- load.dataset()
#diss.mat <- get.diss.matrix(vacan, params$max.row)

#params <- list(max.row=2000, k=5, min.feature.occurences=0.05,
#               max.feature.pval=0.05, cached.diss.mat=TRUE)
#params$diss.mat <- diss.mat

# Perform training and evaluationg
#train.res <- train.kmean.lm(params, vacan)  # this might save time
#residuals <- evaluate.train.kmean.lm(train.res[[2]])

# Plot residuals
#boxplot(residuals, horizontal = TRUE, main='Residuals')
#abline(v=(seq(-200000,500000,10000)), col="lightgray", lty="dotted")
