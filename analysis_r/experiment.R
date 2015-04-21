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