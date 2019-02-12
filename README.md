# Sentida
Sentida is a Danish sentiment analysis tool. Sentida sentiment-scores sentences by the word, and gives either a mean sentiment score or a total score. Sentida uses sophisticated methods to take adverb-modifiers, exclamation marks and negations into account when sentiment-scoring. 

# Downloading Sentida for the first time

if(!require("devtools")) install.packages("devtools")

devtools::install_github("Guscode/Sentida")

library(Sentida) 

# Using Sentida

The sentida function takes in a string and an output argument. The output argument can be the default "total" or "mean".
Output = "total" will provide an accumulated sentiment score for the string.
Output = "mean" will provide a mean sentiment score per word in the string.

# Examples

Sentida in a political context:

Total score:
sentida("Abort er mord", output = "total") -> -4.67

Mean score:
sentida("Abort er mord", output = "mean") -> -1.56

Effect of exclamation mark:
sentida("Abort er mord!", output = "total") -> -6.02


Sentida in a commercial context:

Total score:
sentida("Colgate er godt og smager dejligt", output = "total") -> 5

Effect of adverb modifiers:
sentida("Colgate er godt og smager mega dejligt", output = "total") -> 5.8
