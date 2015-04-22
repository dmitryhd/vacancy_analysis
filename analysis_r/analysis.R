
load_dataset <- function() {
  vacan <- read.csv("~/repos/vacancy_analysis/analysis_r/vacan_exp.csv", sep=";", stringsAsFactors=FALSE)
  vacan$X <- NULL
  num_vars <- c('max_sal', 'min_sal', 'max_exp', 'min_exp')
  for (field in num_vars) {
    vacan[[field]] <- suppressWarnings(as.numeric(vacan[[field]]))
  }
  tmp <- vacan[!names(vacan) %in% num_vars]
  vacan <- vacan[rowSums(tmp) != 0,]
  vacan$min_exp[is.na(vacan$min_exp)] <- 0
  vacan$max_exp[is.na(vacan$max_exp)] <- 0
  vacan
}

make_categories <- function(vacan, bin.number) {
  # fill NAs in salary: if min NA, set to max, if max is NA, set to min
  vacan$min_sal[is.na(vacan$min_sal)] <- vacan$max_sal[is.na(vacan$min_sal)]
  vacan$max_sal[is.na(vacan$max_sal)] <- vacan$min_sal[is.na(vacan$max_sal)]
  vacan$mean_sal <- vacan$min_sal + (vacan$max_sal - vacan$min_sal)/2
  norm_sal <- vacan$mean_sal
  bin.size <- (max(norm_sal, na.rm=TRUE) - min(norm_sal, na.rm=TRUE) ) / bin.number
  vacan$category <- as.integer((norm_sal -  min(norm_sal, na.rm=TRUE))/ bin.size)
  vacan
}

jaccard_metric <- function(a, b) {
  dist <- 1 - sum(a & b) / sum(a | b)
  if(is.nan(dist)) {
    dist <- 1
  }
  dist
}

get_dissimilarity_martix <- function(proc.vacan) {
  # TODO: too long use library(bit)
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
      mat[row, col] <- jaccard_metric(bitmap[[col]], bitmap[[row]])
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
  mat
}

get_vector <- function(x) {
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

set_score <- function(x, w, min_exp_w, max_exp_w) {
  scores <- c()
  for (i in 1:dim(x)[1]){
    y <- get_vector(x[i,])
    score <- sum(y*w) + x[i,]$min_exp * min_exp_w + x[i,]$max_exp * max_exp_w
    scores <- c(scores, score)
  }
  x$score <- scores
  x
}

get_w <- function(cur_clust, money_weight) {
  w <- rep(0, dim(cur_clust)[2] - 7)
  for (cat in unique(cur_clust$category)) {
    cur_cat <- cur_clust[cur_clust$category==cat,]
    cur_cat <- get_vector(cur_cat)
    cur_cat_weights <- colSums(cur_cat)
    cur_cat_weights <- cur_cat_weights * (cat * money_weight)
    #cat('category', cat)
    #print(as.numeric(cur_cat_weights))
    w <- w + cur_cat_weights
  }
  w
}

perform_experiment <- function(money_weight, min_exp_w, max_exp_w, clust.num=1, category.num=5) {
  # CLASSIFICATION BY MONEY
  # GETTING WEIGHTS
  # SCORING
  # REGRESSION
  cur_clust <- small[small$clust == clust.num,]
  cur_clust <- make_categories(cur_clust, category.num)
  w <- get_w(cur_clust, money_weight)
  print(as.numeric(w))
  cur_clust <- set_score(cur_clust, w, min_exp_w, max_exp_w)
  plot(cur_clust$score, cur_clust$mean_sal, main='expriment')
  x<-lm(cur_clust$mean_sal~cur_clust$score)
  print(x)
  abline(x)
}

library(cluster)
library(bit)
# PREPARE DATA
vacan <- load_dataset()
vacan_strip <- get_vector(vacan)
MAX.row <- 2000
train <- vacan_strip[1:MAX.row,]
train.full <- vacan[1:MAX.row,]
diss_mat <- get_dissimilarity_martix(train)

# CLUSTERIZATION
pamx <- pam(diss_mat, k=5, diss=TRUE)
train.full$clustering <- pamx$clustering

#plot(pamx); pamx$clustering #str(small, list.len=120) #dim(small[small$clust == 1,])

# CLASSIFICATION BY MONEY
perform_experiment(1, 7, 40)

proc.vacan[rowSums(proc.vacan) != 0,]
setwd('repos/vacancy_analysis/analysis_r/')

model <- lm(max_sal ~ . , data=cl1)