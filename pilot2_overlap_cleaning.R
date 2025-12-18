library(jsonlite)
library(readr)
library(tidyverse)
library(ggplot2)
library(ggsignif)
library(mlogit)
library(conflicted)

conflict_prefer("select", "dplyr")
conflict_prefer("filter", "dplyr")

# Load data
df <- read.csv("Label Overlap_December 7, 2025_21.40.csv") # Input the actual file name

df <- df %>%
  slice(5:7)
  
# Find the allTrialData column (it might have a different name after export)
# Common variations: "allTrialData", "allTrialData_TEXT", "Q1_allTrialData"
trial_col <- names(df)[grep("allTrialData", names(df), ignore.case = TRUE)]

if (length(trial_col) == 0) {
  stop("Could not find allTrialData column. Check column names above.")
}

print(paste("Found trial data column:", trial_col[1]))

# Function to safely parse JSON for each row
parse_trial_json <- function(json_string) {
  if (is.na(json_string) || json_string == "" || json_string == "allTrialData") {
    return(NULL)
  }
  
  tryCatch({
    trials <- fromJSON(json_string)
    return(trials)
  }, error = function(e) {
    return(NULL)
  })
}

# Parse the JSON column
df$parsed_trials <- lapply(df[[trial_col[1]]], parse_trial_json)

# Remove rows where parsing failed
df_with_data <- df[!sapply(df$parsed_trials, is.null), ]

# Expand the nested data
# Use ResponseId as participant identifier
df_expanded <- df_with_data %>%
  select(-parsed_trials) %>%
  {
    participant_info <- .
    
    # Extract and expand trial data with ResponseId
    trial_data <- df_with_data %>%
      select(ResponseId, parsed_trials) %>%
      rowwise() %>%
      mutate(trials_df = list(parsed_trials %>% mutate(ResponseId = ResponseId))) %>%
      pull(trials_df) %>%
      bind_rows()
    
    # Join participant info with trial data
    trial_data %>%
      left_join(participant_info %>% select(-matches("^parsed_trials$")), by = "ResponseId")
  }

# =============================================================================
# Pivot wider to get one column per trial
# Note: Pivot numeric and character columns separately, then combine
# =============================================================================

# Get the original participant columns (everything except trial data)
participant_cols <- df_with_data %>%
  select(-parsed_trials, -matches("^trial$|size_percent|overlap_percent|response_time|order_indicator|label_left|label_right|field1|field2"))

# Separate numeric and character trial variables
numeric_vars <- c("size_percent", "overlap_percent", "response_time", "order_indicator")
char_vars <- c("label_left", "label_right", "field1", "field2")

# Process numeric variables
df_numeric_wide <- df_expanded %>%
  select(all_of(names(participant_cols)), trial, all_of(numeric_vars)) %>%
  pivot_longer(
    cols = all_of(numeric_vars),
    names_to = "variable",
    values_to = "value"
  ) %>%
  mutate(col_name = paste0("trial_", trial, "_", variable)) %>%
  select(-variable, -trial) %>%
  pivot_wider(
    names_from = col_name,
    values_from = value
  )

# Process character variables
df_char_wide <- df_expanded %>%
  select(all_of(names(participant_cols)), trial, all_of(char_vars)) %>%
  pivot_longer(
    cols = all_of(char_vars),
    names_to = "variable",
    values_to = "value"
  ) %>%
  mutate(col_name = paste0("trial_", trial, "_", variable)) %>%
  select(-variable, -trial) %>%
  pivot_wider(
    names_from = col_name,
    values_from = value
  )

# Combine numeric and character wide formats
# Remove duplicate participant columns from char_wide
char_cols_only <- df_char_wide %>%
  select(-all_of(names(participant_cols)))

df_wide <- bind_cols(df_numeric_wide, char_cols_only)

