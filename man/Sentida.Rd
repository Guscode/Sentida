\name{Sentida}
\alias{Sentida}
%- Also NEED an '\alias' for EACH other topic documented here.
\title{
Sentiment scores a string
}
\description{
sentida sentiment-scores a string of text. 
}
\usage{
sentida(string, output = "total")
}
%- maybe also 'usage' for other objects documented here.
\arguments{
  \item{string:}{A character string
}
  \item{output:}{"total" for total score, "mean" for mean score
  }
}
\examples{
# Examples of sentiment scoring

library(sentida)

# Score danish words
sentida("gud bevare Danmark")
}

