
crossvalidation <- function(data.set, perform.train, evaluate.test, n, maxit=n) {
  # n - is number of subsets
  # returns errors
  m <- nrow(data.set)
  residuals <- c()
  set.seed(1)
  # shuffle data
  data.set <- data.set[sample(m),]
  for (it in 1:maxit) {
    # get train and test set
    test.indices <- get.test(it, n, m)
    test <- data.set[test.indices,]
    train <- data.set[get.train(test.indices, m),]
    train.res <- perform.train(train)
    cat('train', it,' done, evaluating residuals\n')
    residuals <- c(residuals, evaluate.test(train.res, test))
  }
  residuals
}

get.test <- function(iteration, n, m) {
  bin.size <- as.integer(m / n)
  begin <- 1 + (iteration-1)*bin.size
  end <- (iteration)*bin.size
  begin:end
}

get.train <- function(test, m) {
  train <- 1:m
  train[-test]
}
