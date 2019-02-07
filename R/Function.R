#' Sentiment scores a string
#'
#' @name Sentida
#'
#' @param string: a text string
#'
#' @description
#' Sentida sentiment-scores a string of text. It uses the AFINN sentiment scoring. It assigns a value to each recognized word or emoticon in the string and returns the sum.
#'
#' @return
#' The function returns the sum of sentiment.
#'
#' @export
#'

sentida <- function(string){
  intense <- 1
  score <- 0
  rev <- 0
  wordsc <- 0
  mul <- 0
  string <- as.character(string)
  string <- tolower(string)
  space <- strsplit(string, "")[[1]]
  string <- str_replace_all(string, "[[:punct:]]", "")
  if (" " %in% space){
    realstr <- strsplit(string, " ")[[1]]
  } else {
    realstr <- string
  }
  if ("!" %in% space){
    intense <- 1.29
  }
  realstr <- wordStem(realstr, language = "danish")
  for (word in realstr){
    if (word == "ikk"){
      rev <- 3
    }
    if (word %in% intensifier$stem){
      mul <- 2
      multiplier <- intensifier$score[which(intensifier$stem == word)]
    }
    if (word %in% aarup$stem){
      wordsc <-  aarup$score[which(aarup$stem == word)]
      if (rev == 1 | rev == 2){
        wordsc <- wordsc*(-1)
      }
      
      if (mul == 1){
        wordsc <- wordsc*multiplier
      }
      score <- score+wordsc
      
    } else {
      score <- score + 0
    }
    if (rev != 0){
      rev <- rev-1 
    }
    if (mul != 0){
      mul <- mul - 1
    }
  }
  return(score*intense)
}
