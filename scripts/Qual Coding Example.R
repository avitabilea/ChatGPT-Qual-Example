# -------------------------------------------------------------------
# Author: Andrew Avitabile
# Purpose: General function to that uses ChatGPT to code things
# -------------------------------------------------------------------

# ---- Setup ----
rm(list = ls())
# You'll need to install the pacman package and these below:
pacman::p_load("httr", "jsonlite", "tidyverse", "progress")

# -------------------------------------------------------------------
# Function: call_chatgpt_batch()
# -------------------------------------------------------------------
# Description:
#   Takes a dataset and a text column, sends each unique text value to
#   the ChatGPT API using a user-defined prompt, and returns responses.
#
# Arguments:
#   data       - data frame containing text to classify
#   text_col   - column name (string) of text input
#   prompt_fn  - function that builds the prompt given one text value
#   model      - OpenAI model to use (e.g., "gpt-4o-mini", "gpt-3.5-turbo")
#   api_key    - your OpenAI API key (you'll need to get this by making an account at https://openai.com/. 
#                Try to keep this a secret, as it can be used to bill your account. Consider saving in .Renviron file)
#   start_item - index to resume from (useful for long lists)
#   batch_n    - number of items per batch (for progress tracking and in case the code breaks)
#
# Returns:
#   Original data joined with model responses
# -------------------------------------------------------------------

call_chatgpt_batch <- function(data,
                               text_col,
                               prompt_fn,
                               model = "gpt-4o-mini",
                               api_key = Sys.getenv("OPENAI_API_KEY"),
                               start_item = 1,
                               batch_n = 100) {
  
  # Get unique text values
  texts <- unique(data[[text_col]])
  total <- length(texts)
  
  if (start_item > 1) {
    texts <- texts[start_item:total]
    cat("Resuming from item", start_item, "| Remaining:", length(texts), "\n")
  }
  
  cat("Total unique texts:", total, "| Processing in batches of", batch_n, "\n")
  
  # --- Helper function to call API for one item ---
  get_response <- function(text_value) {
    prompt <- prompt_fn(text_value)
    
    res <- httr::POST(
      url = "https://api.openai.com/v1/chat/completions",
      httr::add_headers(Authorization = paste("Bearer", api_key)),
      httr::content_type_json(),
      body = jsonlite::toJSON(list(
        model = model,
        messages = list(list(role = "user", content = prompt)),
        temperature = 0
      ), auto_unbox = TRUE)
    )
    
    result <- httr::content(res, as = "parsed")
    output <- result$choices[[1]]$message$content
    return(trimws(output))
  }
  
  # --- Process all items ---
  all_results <- tibble()
  
  for (batch_num in 1:ceiling(length(texts) / batch_n)) {
    start_idx <- (batch_num - 1) * batch_n + 1
    end_idx <- min(batch_num * batch_n, length(texts))
    batch_texts <- texts[start_idx:end_idx]
    
    cat("\nProcessing batch", batch_num, "(", length(batch_texts), "items)\n")
    
    pb <- progress_bar$new(
      format = "[:bar] :current/:total (:percent)",
      total = length(batch_texts), clear = FALSE, width = 60
    )
    
    batch_responses <- sapply(batch_texts, function(x) {
      out <- tryCatch(get_response(x), error = function(e) NA)
      pb$tick()
      return(out)
    }, USE.NAMES = TRUE)
    
    batch_df <- tibble(!!text_col := names(batch_responses),
                       model_response = unname(batch_responses))
    
    all_results <- bind_rows(all_results, batch_df)
  }
  
  # Join back with original data
  data_joined <- left_join(data, all_results, by = text_col)
  
  cat("\n✅ All batches complete.\n")
  return(data_joined)
}

# -------------------------------------------------------------------
# Toy Example (ready to run)
# -------------------------------------------------------------------
toy_data <- tibble(item = c("Apple", "Carrot", "Strawberry", "Broccoli"))

toy_prompt <- function(food) {
  paste0("Is '", food, "' a fruit or a vegetable? Respond with only one word: 'fruit' or 'vegetable'.")
}

toy_results <- call_chatgpt_batch(
  data = toy_data,
  text_col = "item",
  prompt_fn = toy_prompt,
  model = "gpt-4o-mini",
  batch_n = 10
)

print(toy_results)


# -------------------------------------------------------------------
# Toy Example (ready to run)
# -------------------------------------------------------------------
# Example data: 3 policies
toy_data <- tibble(item = c(
  # 1. Has explicit number
  "Paternity Leave The school recognizes the importance of supporting employees in balancing their professional responsibilities with the arrival of a new child. Eligible employees are entitled to up to four weeks of paternity leave following the birth, adoption, or placement of a child.",
  
  # 2. Mentions leave but no number
  "The school offers paternity leave to support new parents in caring for their child and adjusting to family routines. Employees should contact HR for eligibility and details.",
  
  # 3. No mention of paternity leave
  "The school encourages professional development and provides up to five days of paid leave per year for attending educational workshops."
))

# Prompt: detect mention + extract number (or 0/NA)
toy_prompt <- function(policy) {
  paste0(
    "You are a careful qualitative researcher. ",
    "Read the policy text below and do the following:\n",
    "1. If the policy mentions paternity leave, extract the number of days it provides.\n",
    "2. If it mentions paternity leave but no number is stated, return 0.\n",
    "3. If it does not mention paternity leave at all, return NA.\n",
    "Convert weeks or months to days (7 days per week, 30 days per month).\n",
    "Respond ONLY with a single number (e.g., 28, 0, or NA).\n\n",
    policy
  )
}

# Call the general function
toy_results <- call_chatgpt_batch(
  data = toy_data,
  text_col = "item",
  prompt_fn = toy_prompt,
  model = "gpt-4o-mini",
  batch_n = 10
)

print(toy_results)