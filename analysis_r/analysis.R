
remove_outliers <- function(x, na.rm = TRUE, ...) {
  qnt <- quantile(x, probs=c(.02, .98), na.rm = na.rm, ...)
  H <- 1.5 * IQR(x, na.rm = na.rm)
  y <- x
  y[x < (qnt[1] - H)] <- NA
  y[x > (qnt[2] + H)] <- NA
  y
}

load_dataset <- function() {
  vacan <- read.csv("~/repos/vacancy_analysis/analysis_r/vacan.csv", sep=";", stringsAsFactors=FALSE)
  vacan$max_sal <- as.numeric(vacan$max_sal)
  vacan$min_sal <- as.numeric(vacan$min_sal)
  vacan$X <- NULL
  vacan
}

make_categories <- function(vacan, bin.number) {
  # fill NAs in salary: if min NA, set to max, if max is NA, set to min
  vacan$min_sal[is.na(vacan$min_sal)] <- vacan$max_sal[is.na(vacan$min_sal)]
  vacan$max_sal[is.na(vacan$max_sal)] <- vacan$min_sal[is.na(vacan$max_sal)]
  vacan$mean_sal <- vacan$min_sal + (vacan$max_sal - vacan$min_sal)/2
  norm_sal <- remove_outliers(vacan$mean_sal)
  bin.size <- (max(norm_sal, na.rm=TRUE) - min(norm_sal, na.rm=TRUE) ) / bin.number
  print(bin.size)
  vacan$category <- as.integer(norm_sal / bin.size)
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

estimate_classification <- function(seed=1, given.k=1, bin.number=10) {
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

print_classification_error <- function(bin.number=10, k=1) {
  err <- estimate_classification(seed=1, given.k=k, bin.number)
  err_stat <- ecdf(err)
  plot(err_stat, main = paste0('Error, k=', k, ', bin=', bin.number))
}

print_classification_error(10, 1)
print_classification_error(15, 1)
print_classification_error(15, 2)
print_classification_error(15, 4)
print_classification_error(15, 6)
print_classification_error(15, 8)
print_classification_error(15, 10)
print_classification_error(15, 20)
