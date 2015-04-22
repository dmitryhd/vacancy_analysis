
load_dataset <- function() {
  vacan <- read.csv("~/repos/vacancy_analysis/analysis_r/vacan_exp.csv", sep=";", stringsAsFactors=FALSE)
  vacan$max_sal <- suppressWarnings(as.numeric(vacan$max_sal))
  vacan$min_sal <- suppressWarnings(as.numeric(vacan$min_sal))
  vacan$max_exp <- suppressWarnings(as.numeric(vacan$max_exp))
  vacan$min_exp <- suppressWarnings(as.numeric(vacan$min_exp))
  vacan$min_exp[is.na(vacan$min_exp)] <- 0
  vacan$max_exp[is.na(vacan$max_exp)] <- 0
  vacan$X <- NULL
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

print_classification_error <- function(w, bin.number=10, k=1) {
  err <- estimate_classification(w, seed=1, given.k=k, bin.number)
  err_stat <- ecdf(err)
  plot(err_stat, main = paste0('Error, k=', k, ', bin=', bin.number))
  cat('Classification error with parameters k = ', k, ' bin.number = ',
      bin.number, ' is ', mean(err, rm.na=TRUE))
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
  mat <- matrix(, nrow = len, ncol = len)
  for(column in 1:len){
    mat[, column] <- rep(NA, len)
  }
  for(col in 1:len) {
    for(row in 1:len) {
      mat[row, col] <- jaccard_metric(proc.vacan[col,], proc.vacan[row,])
    }
    cat("\r", 'calc col:', col)
  }
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

# PREPARE DATA
MAX.row <- 50
vacan <- load_dataset()
vacan_strip <- get_vector(vacan)
diss_mat <- get_dissimilarity_martix(vacan_strip[1:MAX.row,])


# CLUSTERIZATION
library(class)
pamx <- pam(diss_mat, k=5, diss=TRUE)
#plot(pamx); pamx$clustering #str(small, list.len=120) #dim(small[small$clust == 1,])

# CLASSIFICATION BY MONEY
perform_experiment(1, 7, 40)