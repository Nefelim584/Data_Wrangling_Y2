# Exploring Global Video Game Sales

## About the Project

In this project, you will explore and analyze a dataset of global video game sales to uncover trends and insights in the gaming industry.

The dataset contains information on video games released across various platforms, genres, and publishers, along with their sales in different global regions.

Your task is to perform a complete **data wrangling and exploratory data analysis (EDA)** workflow.

---

## Part I: Data Cleaning and Preparation

1. Load the dataset and inspect its structure.
2. Check for missing or inconsistent values.
3. Handle missing data appropriately; decide whether to impute, drop, or leave it as is.
4. Ensure columns have appropriate data types.
5. Check for duplicates and remove them if necessary.

---

## Part II: Exploratory Data Analysis (EDA)

### 1. Descriptive Statistics

1. Compute key descriptive statistics for numerical variables.
2. Identify the top 10 best-selling games globally.

### 2. Trends Over Time

1. Analyze the number of games released per year.
2. Plot global sales over time. Are sales increasing or decreasing?

### 3. Genre Analysis

1. Which genres are most common?
2. Which genres generate the most global sales?

### 4. Platform Analysis

1. What are the most popular platforms by number of games and total sales?
2. How has platform popularity changed over time?

### 5. Regional Analysis

1. Compare preferences between North America, Europe, and Japan.
2. Are there genres that dominate in one region but not others?

### 6. Publisher Insights

1. Identify the top 10 publishers by total global sales.
2. Is there a *hit publisher* that dominates certain genres?

### 7. Market Dominance Analysis

Create a **Market Power Index** for each publisher that considers multiple factors.

#### Step 1: Calculate Genre Market Share

- Calculate each publisher's market share within each genre:

  `Publisher's genre sales / Total genre sales`

- Identify whether a publisher is a **genre leader**, defined as having more than 30% market share in that genre.

#### Step 2: Calculate Publisher Metrics

For each publisher, compute the following metrics:

- **Genre Diversity Score:** The number of different genres they publish in.
- **Regional Consistency Score:** The standard deviation of their sales proportions across regions. Lower values indicate more consistent regional performance.
- **Hit Rate:** The percentage of their games that sold above the median for their respective genres.

#### Step 3: Create the Market Power Index

1. Create a final Market Power Index using a custom formula that combines these metrics.
2. Rank publishers and identify different publisher archetypes, such as:
   - **Genre Specialists**
   - **Diversified Giants**

### 8. Regional Preference Divergence

Identify games and genres that have dramatically different appeal across regions.

#### Step 1: Calculate Regional Divergence Scores

For each game:

1. Normalize each region's sales as a proportion of that game's total sales.
2. Compare each region's proportion with the global average proportion for that region.
3. Use a custom function to calculate divergence, such as a coefficient of variation or an entropy-based measure.

#### Step 2: Create Genre-Region Affinity Scores

1. For each genre, calculate the percentage of its total sales that come from each region.
2. Compare this distribution with the overall regional distribution across all genres.
3. Identify **over-indexed** and **under-indexed** genre-region combinations.

#### Step 3: Identify Temporal Shifts in Regional Preferences

1. Group the data by year and region.
2. Calculate each region's favorite genre per year.
3. Track how regional preferences have converged or diverged over time.
4. Apply a custom function to calculate a **Preference Stability Index** for each region.

#### Step 4: Find Cultural Outliers

1. Identify games that sold exceptionally well in one region (more than 50% of sales) but poorly in others (less than 10% of sales in each).
2. Calculate a **Cultural Specificity Score** for each game.

---

## Part III: Visualization and Storytelling

Use **Matplotlib** or **Seaborn** to visualize your findings.

The plots should:

- Have clear titles, axis labels, and legends.
- Use appropriate plot types.
- Highlight key insights discovered during the EDA.

### Example Visualizations

- Global sales trends over the years.
- Bar chart of top-selling genres.
- Heatmap comparing regional sales by genre.
- Publisher versus total global sales.
- Platform evolution over the years.

---

## Deliverables

### 1. Jupyter Notebook

A Jupyter Notebook containing:

- Clean, well-commented code.
- Explanatory text cells for each section.
- Visualizations accompanied by insights.

### 2. Short Conclusion

A short conclusion summarizing:

- The key insights you discovered.
- The data wrangling challenges you faced.
- How visualization helped you better understand the dataset.


Before starting

- Generate csv table with such fuilds:
  - EPIC (List of EPICS for the project, not more than 7)
  - User story (list of user stories in format US_1.1.1)
  - Features (list of features)
  -Dev tasks (list of Dev tasks)
Rules:
- Each EPIC has:
  - Name (E.g - EPIC 1: International Survey Data Ingestion)
  - List of connected Features (not more than 5)
- Each User story has:
  - Name (E.g - US 1.1.1)
  - Description (E.g - As a Data Engineer, I want to automatically ingest the French Excel survey files so that French satisfaction data is available on the centralized platform.)
  - Connection to the correct EPIC (E.g - User stories from 1.1.1 to 1.5.1 are connected to the EPIC 1)
- Each Feature has:
  - Name (E.g - FEAT 1.1: France Excel Ingestion)
  - Connection to the selected User story (E.g - FEAT 1.1 connects to the US_1.1.1, FEAT 1.2 connects to the US_1.2.1 and etc.)
  - List of Dev tasks associated with this feature (not more than 4)
- Each Dev task has:
  - Name (E.g - Create sample France Excel survey file and identify source columns (survey_id, date, product, service, rating).)
  - Corresponding Feature 
