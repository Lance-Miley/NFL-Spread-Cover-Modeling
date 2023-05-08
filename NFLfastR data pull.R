library(nflfastR)
library(dplyr, warn.conflicts = FALSE)
pbp <- nflfastR::load_pbp(2008:2022)
games_2008_2022 <- pbp
write.csv(games_2008_2022, file = "2008-2022.csv")
