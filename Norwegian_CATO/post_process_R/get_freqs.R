## ----
library(tidyverse)
library(magrittr)

options(scipen=0)

Dfall <- read_delim("./resources/tidy_1gram_nob_abc.txt", '\t') 


# identify closed class gives closed == NA for open class
Dfall %<>% left_join(unique(read_csv("./resources/closed_nor.txt", col_names = FALSE) %>% 
                        rename(fword = 1) %>% 
                        mutate(closed = T)))

#add word lengths
Dfall %<>% 
  mutate(leng = nchar(fword))

max_wd_length = 9
min_wd_length = 3

## ----
# select just some words
Df <- Dfall %>% 
  filter(freq > 10000
         ,leng >= min_wd_length
         ,leng <= max_wd_length
         ,is.na(closed)) %>%
  select(fword, freq)
  
Df %>% count()

# set letters in columns
Df <- cbind(Df,str_split_fixed(Df$fword, '',max_wd_length)) %>% 
  rename_at(vars('1':'9'), list(function(x){paste0('L',x)}))

# gather to give one letter per row
Df %<>% gather(Letter_N, letter, -fword, -freq) %>% 
  arrange(desc(freq),fword) %>% 
  filter(letter != '')

# get digraphs
Df %<>% 
  group_by(fword) %>% 
  mutate(dig = ifelse(is.na(lead(letter,1)), '', paste0(letter,lead(letter,1)))) %>% 
  # mark letter doubles
  mutate(is_double = ifelse(!is.na(lead(letter,1)) & letter == lead(letter,1), 1, 0) ) %>% 
  ungroup()


# get and apply letter and digraph freqs ----

# letters
freqs <- read_delim("./resources/monstidy_1gram_nob_abc.txt",
                          "\t", escape_double = FALSE, trim_ws = F, col_names = FALSE)

# creates a named vector that can then be used to lookup frequencies
freq_lookup <- freqs$X2
names(freq_lookup) <- freqs$X1
Df %<>% 
  mutate(letter_freq = freq_lookup[letter])

# digraphs
freqs <- read_delim("./resources/digstidy_1gram_nob_abc.txt",
                       "\t", escape_double = FALSE, trim_ws = F, col_names = FALSE) %>% 
  rename(dig = X1, dig_frq = X2) %>% 
  # get conditional probabilities. e.g., if current letter is 'a' what is the
  # probability that the next letter is 'b'
  mutate(dig1 = str_split_fixed(dig,'', n=2)[,1]) %>% 
  group_by(dig1) %>% 
  mutate(dig1_frq = sum(dig_frq),
         dig_frq_cond = dig_frq/dig1_frq) %>% 
  ungroup() %>% 
  arrange(dig) %>% 
  select(-dig1, -dig1_frq)

freq_lookup <- freqs$dig_frq
names(freq_lookup) <- freqs$dig
Df %<>% 
  mutate(dig_freq = freq_lookup[dig])

freq_lookup <- freqs$dig_frq_cond
names(freq_lookup) <- freqs$dig
Df %<>% 
  mutate(dig_condprob = freq_lookup[dig])

rm(Dfall, freqs, freq_lookup)

# by-word summaries ----

freqs_byword <- Df %>% 
  group_by(fword) %>% 
  summarise(word_len = max(nchar(fword))
            ,freq = max(freq)
            ,has_double = ifelse(sum(is_double) > 0, 1, 0)
            ,M_letter_freq = mean(letter_freq)
            ,init_letter_freq = letter_freq[Letter_N == 'L1']
            ,M_dig_freq = mean(dig_freq, na.rm = T)
            ,init_dig_freq = dig_freq[Letter_N == 'L1']
            ,M_dig_condprob = mean(dig_condprob, na.rm = T)
            ,init_dig_condprob = dig_condprob[Letter_N == 'L1']) %>%
  arrange(word_len, desc(freq))
  
library(openxlsx)
write.xlsx(freqs_byword, 'tmp.xlsx')
