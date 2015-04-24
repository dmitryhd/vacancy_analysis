# There represented some models for regression inside of cluster.

weighted_category_estimation <- function() {
    make_categories <- function(vacan, bin.number) {
        # fill NAs in salary: if min NA, set to max, if max is NA, set to min

        norm_sal <- vacan$mean_sal
        bin.size <- (max(norm_sal, na.rm=TRUE) - min(norm_sal, na.rm=TRUE) ) / bin.number
        vacan$category <- as.integer((norm_sal -  min(norm_sal, na.rm=TRUE))/ bin.size)
        vacan
    }  
    
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
    #print(as.numeric(w))
    cur_clust <- set_score(cur_clust, w, min_exp_w, max_exp_w)
    plot(cur_clust$score, cur_clust$mean_sal, main='expriment')
    x<-lm(cur_clust$mean_sal~cur_clust$score)
    #print(x)
    abline(x)
}

# CLASSIFICATION BY MONEY
#perform_experiment(1, 7, 40)