
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

category_to_salary <- function(category, bin.size) {
  category * bin.size
}

make_categories <- function(vacan) {
  # fill NAs in salary: if min NA, set to max, if max is NA, set to min
  vacan$min_sal[is.na(vacan$min_sal)] <- vacan$max_sal[is.na(vacan$min_sal)]
  vacan$max_sal[is.na(vacan$max_sal)] <- vacan$min_sal[is.na(vacan$max_sal)]
  vacan$mean_sal <- vacan$min_sal + (vacan$max_sal - vacan$min_sal)/2
  norm_sal <- remove_outliers(vacan$mean_sal)
  bin.number <- 10
  bin.size <- (max(norm_sal, na.rm=TRUE) - min(norm_sal, na.rm=TRUE) ) / bin.number
  vacan$category <- as.integer(norm_sal / bin.size)
  #cl <- factor(vacan.category)
  vacan
}


shuffle_data <- function(vacan, seed=1) {
  set.seed(seed)
  x2 <- vacan[sample.int(dim(vacan)[1]),]
  x2
}

get_train <- function(vacan) {
  upper <- dim(vacan)[1]*.9
  train <- vacan[1:upper,]
  train[is.na(train$category)]$category <- 11
  train
}

get_test <- function(vacan) {
  lower <- dim(vacan)[1]*.9
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

# data preparation

vacan <- load_dataset()
vacan <- make_categories(vacan)
train_and_test <- create_training_sample(vacan, 1)
train <- train_and_test[[1]]
test <- train_and_test[[2]]

cl <- factor(train$category)
strip_train <- strip_set(train)
strip_test <- strip_set(test)
valid <- test$category

# classification

library(class)
cl[is.na(cl)] <- 0 # TODO - move
result <- knn(strip_train, strip_test, cl, k = 10) 
summary(result)
calculate_precision(test$category, as.integer(result))

errors <- abs(test$category - as.integer(result))
errors_stat <- ecdf(errors)
plot(errors_stat)



calculate_precision <- function(expected, result) {
  sum(expected - result == 0)/length(expected)
}


