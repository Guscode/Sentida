#' Sentiment scores a string
#'
#' @name sentida
#'
#' @param string a text string
#' @param output "total" for total score, "mean" for mean score
#'
#'
#' @description
#' Sentida sentiment-scores a string of text.
#'
#' @return
#' The function returns the sum of sentiment.
#'
#' @examples
#'
#' sentida("Gud bevare Danmark")
#'
#'
#'
#' @export sentida



sentida <- function(string, output = "total"){
  sys_name <- Sys.info()["sysname"][[1]]
  intense <- 1
  score <- 0
  rev <- 0
  word_cont <- 0
  wordsc <- 0
  mul <- 0
  realstr <- c()
  acclist <- c(0)
  string <- as.character(string)
  string <- tolower(string)
  space <- stringr::str_split(string, "")[[1]]
  string <- stringr::str_replace_all(string, "[[:punct:]]", "")
  if (" " %in% space){
    firststring <- stringr::str_split(string, " ")[[1]]
    for (word in firststring){
      if (word != ""){
        realstr <- c(realstr, word)
      }
    }
  } else {
    realstr <- string
  }
  if ("!" %in% space){
    intense <- 1.29
  }
  realstr <- SnowballC::wordStem(realstr, language = "danish")
  for (word in realstr){
    if (word == "ikk"){
      rev <- 3
    }
    if (word %in% intensifier$stem){
      mul <- 2
      multiplier <- intensifier$score[which(intensifier$stem == word)]
    }
    if (fastmatch::fmatch(word, aarup$stem, nomatch = 0L) > 0L){
      if (sys_name == "Windows"){
      wordsc <-  get(word ,envir=env, inherits=FALSE)}
      else {wordsc <- aarup$score[which(aarup$stem == word)]}
      word_cont <- word_cont +1
      if (rev == 1 | rev == 2){
        wordsc <- wordsc*(-1)
      }
      if (mul == 1){
        wordsc <- wordsc*multiplier
      }
      score <- score+wordsc

    } else {
      score <- score
    }
    if (rev != 0){
      rev <- rev-1
    }
    if (mul != 0){
      mul <- mul - 1
    }
  }
  score <- score*intense
  if (output == "mean"){
    if (word_cont == 0){
      score == 0
    } else {
      score <- score/word_cont
    }
    return(score)
  }
  if (output == "total"){
    return(score)
  }
}



