
remove_outliers <- function(x, na.rm = TRUE, ...) {
  qnt <- quantile(x, probs=c(.25, .75), na.rm = na.rm, ...)
  H <- 1.5 * IQR(x, na.rm = na.rm)
  y <- x
  y[x < (qnt[1] - H)] <- NA
  y[x > (qnt[2] + H)] <- NA
  y
}

load_dataset <- function() {
  vacan <- read.csv("~/repos/vacancy_analysis/analysis_r/vacan.cvs", sep=";", stringsAsFactors=FALSE)
  vacan$max_sal <- as.numeric(vacan$max_sal)
  vacan$min_sal <- as.numeric(vacan$min_sal)
  vacan
}

sample_plot <- function() {
  ds <- load_dataset()
  x <- ds$max_sal
  x <- remove_outliers(x)
  hist(x, breaks=20)
}