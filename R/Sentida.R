#' Sentiment scores a string
#'
#' @name Sentida
#'
#' @param string: a text string
#' @param outout: "total" for total score, "mean" for mean score
#'
#' @description
#' Sentida sentiment-scores a string of text.
#'
#' @return
#' The function returns the sum of sentiment.
#'
#' @export
#'


sentida <- function(string, output = "total"){
  intense <- 1
  score <- 0
  rev <- 0
  wordsc <- 0
  mul <- 0
  string <- as.character(string)
  string <- tolower(string)
  space <- stringr::str_split(string, "")[[1]]
  string <- stringr::str_replace_all(string, "[[:punct:]]", "")
  if (" " %in% space){
    realstr <- stringr::str_split(string, " ")[[1]]
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
    if (word %in% aarup$stem){
      wordsc <-  aarup$score[which(aarup$stem == word)]
      if (rev == 1 | rev == 2){
        wordsc <- wordsc*(-1)
      }
      if (wordint %in% intensifier$stem){
        mul <- 2
        multiplier <- intensifier$score[which(intensifier$stem == word)]
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
score <- score*intense
if (output == "mean"){
  score <- score/length(realstr)
  return(score)
}
if (output == "total"){
  return(score)
}

}
