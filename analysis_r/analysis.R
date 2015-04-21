
remove_outliers <- function(x, na.rm = TRUE, ...) {
  qnt <- quantile(x, probs=c(.02, .98), na.rm = na.rm, ...)
  H <- 1.5 * IQR(x, na.rm = na.rm)
  y <- x
  y[x < (qnt[1] - H)] <- NA
  y[x > (qnt[2] + H)] <- NA
  y
}

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
  #norm_sal <- remove_outliers(vacan$mean_sal)
  norm_sal <- vacan$mean_sal
  bin.size <- (max(norm_sal, na.rm=TRUE) - min(norm_sal, na.rm=TRUE) ) / bin.number
  print(bin.size)
  vacan$category <- as.integer((norm_sal -  min(norm_sal, na.rm=TRUE))/ bin.size)
  #cl <- factor(vacan.category)
  #vacan[is.na(vacan$category)]$category <- 0
  vacan
}


shuffle_data <- function(vacan, seed=1) {
  set.seed(seed)
  x2 <- vacan[sample.int(dim(vacan)[1]),]
  x2
}

get_train <- function(vacan) {
  upper <- dim(vacan)[1]*.8
  train <- vacan[1:upper,]
  train
}

get_test <- function(vacan) {
  lower <- dim(vacan)[1]*.8
  upper <- dim(vacan)[1]
  test <- vacan[lower:upper,]
  test
}

create_training_sample <- function(vacan, seed=1) {
  # return train, test
  shuffled <- shuffle_data(vacan, seed)
  list(get_train(shuffled), get_test(shuffled))
}

strip_set <-function(set) {
  stripped <- set
  stripped$max_sal <- NULL
  stripped$min_sal <- NULL
  stripped$mean_sal <- NULL
  stripped$category <- NULL
  stripped
}

library(class)

estimate_classification <- function(w, seed=1, given.k=1, bin.number=10) {
  # data preparation
  vacan <- load_dataset()
  vacan <- make_categories(vacan, bin.number)
  train_and_test <- create_training_sample(vacan, seed)
  train <- train_and_test[[1]]
  test <- train_and_test[[2]]
  
  # classification
  cl <- factor(train$category)
  strip_train <- strip_set(train)
  strip_test <- strip_set(test)
  valid <- test$category
  
  # estimatin
  cl[is.na(cl)] <- 0 # TODO - move
  result <- knn(strip_train, strip_test, cl, k=given.k) 
  errors <- abs(test$category - as.integer(result))
  errors
}

print_classification_error <- function(w, bin.number=10, k=1) {
  err <- estimate_classification(w, seed=1, given.k=k, bin.number)
  err_stat <- ecdf(err)
  plot(err_stat, main = paste0('Error, k=', k, ', bin=', bin.number))
  cat('Classification error with parameters k = ', k, ' bin.number = ',
      bin.number, ' is ', mean(err, rm.na=TRUE))
}

get_weights <- function(vacan) {
  # TODO: optimize
  vacan2 <-vacan
  vacan2$max_sal <- NULL
  vacan2$min_sal <- NULL
  vacan2$mean_sal <- NULL
  total_weights <- rep(0, dim(vacan2)[2]-1)
  for (category in 1:10) {
    weights <- rep(0, dim(vacan2)[2]-1)
    r <- vacan2[vacan2$category == category, !(names(vacan2) %in% c("category"))]
    r <- r[complete.cases(r), ]
    for (i in 1:dim(r)[1]) {
        weights <- weights + r[i,]
    }
    weights <- weights / dim(r)[1]
    if (! is.na(category)) {
      weights <- weights * category
    }
    total_weights <- total_weights + weights
  }
  total_weights
}

jaccard_metric <- function(a, b) {
  dist <- 1 - sum(a & b) / sum(a | b)
  if(is.nan(dist)) {
    dist <- 1
  }
  dist
}

get_dissimilarity_martix <- function(proc.vacan){
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

# CLUSTERIZATION
small <- vacan[1:100,]
diss_mat2 <- get_dissimilarity_martix(vacan_strip[1:100,])
pamx <- pam(diss_mat2, k=5, diss=TRUE)
plot(pamx)
pamx$clustering

str(small, list.len=120)
dim(small[small$clust == 1,])

# CLASSIFICATION BY MONEY
# GETTING WEIGHTS
# SCORING
# REGRESSION
get_clust_exp <- function(money_weight, min_exp_w, max_exp_w) {
  cur_clust <- small[small$clust == 1,]
  cur_clust <- make_categories(cur_clust, 5)
  w <- get_w(cur_clust, money_weight)
  print(as.numeric(w))
  cur_clust <- set_score(cur_clust, w, min_exp_w, max_exp_w)
  plot(cur_clust$score, cur_clust$mean_sal)
  x<-lm(cur_clust$mean_sal~cur_clust$score)
  print(x)
  abline(x)
}

#get_clust_exp(1, 100, 200)
get_clust_exp(1, 7, 40)