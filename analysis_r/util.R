not.skill.vars <- c('max_sal', 'min_sal', 'max_exp', 'min_exp')
added.vars <- c('clustering', 'mean_sal', 'category')

clear.data <- function(x) {
  # Delete not significant fields
  for (field in c(added.vars, not.skill.vars)) {
    x[field] <- NULL
  }
  x$R <- NULL
  return(x)
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
  cat('\n')
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
  set$min_sal <- NULL
  set$max_sal <- NULL
  set
}
calculate.mean.exp <- function(set) {
  # Return set with new mean_sal field
  set$min_exp[is.na(set$min_exp)] <- set$max_exp[is.na(set$min_exp)]
  set$max_exp[is.na(set$max_exp)] <- set$min_exp[is.na(set$max_exp)]
  set$mean_exp <- set$min_exp + (set$max_exp - set$min_exp)/2
  set$min_exp <- NULL
  set$max_exp <- NULL
  set
}
