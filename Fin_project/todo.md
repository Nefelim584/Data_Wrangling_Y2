# TODO — Exploring Global Video Game Sales

> Master task list derived from [Proj.md](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/Fin_project/Proj.md)

---

## Phase 1: Project Setup & Dataset Acquisition

- [x] Create the project directory structure and initialize the Jupyter Notebook
- [x] Locate or download the global video game sales dataset (e.g., `vgsales.csv`)
- [x] Set up a Python virtual environment and install required libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`)
- [x] Add introductory markdown cells to the notebook explaining the project goal
- [x] Verify the dataset file is accessible and readable from the notebook

---

## Phase 2: Data Loading & Initial Inspection

- [x] Load the dataset into a Pandas DataFrame
- [x] Display the first/last rows and check `.shape`, `.info()`, `.dtypes`
- [x] Examine column names and understand what each column represents
- [x] Generate a quick summary with `.describe()` for numerical columns
- [x] Document initial observations in a markdown cell

---

## Phase 3: Data Cleaning — Missing & Inconsistent Values

- [x] Identify missing values per column using `.isnull().sum()` and visualize them
- [x] Investigate patterns behind the missing data (MCAR / MAR / MNAR)
- [x] Decide on a strategy per column: impute, drop, or leave as-is
- [x] Apply the chosen strategy and verify no unintended data loss occurred
- [x] Check for inconsistent values (e.g., typos in platform/genre/publisher names)
- [x] Standardize any inconsistent categorical values
- [x] Document all cleaning decisions and rationale in markdown cells

---

## Phase 4: Data Type Correction & Duplicate Removal

- [x] Convert columns to appropriate data types (e.g., `Year` to integer/datetime)
- [x] Ensure sales columns are float/numeric
- [x] Ensure categorical columns (`Genre`, `Platform`, `Publisher`) are of type `category` or clean strings
- [x] Check for duplicate rows using `.duplicated()`
- [x] Remove confirmed duplicates and log how many were removed
- [x] Perform a final sanity check on the cleaned DataFrame

---

## Phase 5: Descriptive Statistics & Top-Selling Games

- [x] Compute key descriptive statistics for all numerical variables (mean, median, std, min, max)
- [x] Identify the top 10 best-selling games globally and display them in a table
- [x] Analyze the distribution of global sales (skewness, outliers)
- [x] Summarize notable patterns (e.g., highly skewed sales, dominant outliers)
- [x] Add markdown commentary interpreting the statistics

---

## Phase 6: Trends Over Time

- [x] Analyze the number of games released per year and plot the trend
- [x] Plot global sales aggregated by year (line chart)
- [x] Determine whether sales are increasing, decreasing, or cyclical
- [x] Identify peak years and correlate them with major industry events (console launches, etc.)
- [x] Write insights on temporal trends in a markdown cell

---

## Phase 7: Genre Analysis

- [x] Count games per genre and rank genres by frequency
- [x] Calculate total and average global sales per genre
- [x] Visualize genre distribution (bar chart of game count and sales)
- [x] Identify which genres are most common vs. which generate the most revenue
- [x] Summarize genre-level insights

---

## Phase 8: Platform Analysis

- [x] Rank platforms by number of games released and total sales
- [x] Visualize the most popular platforms (bar charts)
- [x] Analyze how platform popularity has changed over time (line/area chart)
- [x] Identify platform lifecycles (rise, peak, decline)
- [x] Correlate platform trends with console generations
- [x] Document platform insights

---

## Phase 9: Regional Sales Analysis

- [x] Compare total sales across NA, EU, JP, and Other regions
- [x] Calculate regional sales proportions per genre
- [x] Identify genres that dominate in one region but not others
- [x] Visualize regional preferences (grouped bar charts or heatmap)
- [x] Highlight notable regional differences in a markdown cell

---

## Phase 10: Publisher Insights

- [x] Identify the top 10 publishers by total global sales
- [x] Visualize publisher rankings (horizontal bar chart)
- [x] Analyze genre distribution per top publisher
- [x] Determine if any publisher dominates specific genres ("hit publisher")
- [x] Summarize publisher-level findings

---

## Phase 11: Market Dominance — Genre Market Share & Publisher Metrics

- [x] Calculate each publisher's market share within each genre (`publisher genre sales / total genre sales`)
- [x] Flag publishers as **Genre Leaders** where market share exceeds 30%
- [x] Compute **Genre Diversity Score** per publisher (number of distinct genres)
- [x] Compute **Regional Consistency Score** per publisher (std dev of regional sales proportions)
- [x] Compute **Hit Rate** per publisher (% of games selling above the genre median)
- [x] Compile all metrics into a single publisher metrics DataFrame

---

## Phase 12: Market Power Index & Publisher Archetypes

- [x] Design a custom formula combining Genre Diversity, Regional Consistency, and Hit Rate
- [x] Calculate the **Market Power Index** for every publisher
- [x] Rank publishers by the Market Power Index
- [x] Classify publishers into archetypes: **Genre Specialists** vs. **Diversified Giants**
- [x] Visualize the Market Power Index and archetypes (scatter plot or ranked bar chart)
- [x] Document the formula, rankings, and archetype definitions

---

## Phase 13: Regional Preference Divergence — Divergence & Affinity Scores

- [x] Normalize each region's sales as a proportion of each game's total sales
- [x] Compare each game's regional proportions with the global average proportions
- [x] Implement a custom divergence function (coefficient of variation or entropy-based)
- [x] Calculate **Regional Divergence Score** for each game
- [x] For each genre, compute regional sales distribution and compare to the overall distribution
- [x] Identify **over-indexed** and **under-indexed** genre-region combinations
- [x] Create a **Genre-Region Affinity Score** table/heatmap

---

## Phase 14: Temporal Preference Shifts & Cultural Outliers

- [x] Group data by year and region; determine each region's favorite genre per year
- [x] Track how regional genre preferences have converged or diverged over time
- [x] Implement and apply a custom **Preference Stability Index** for each region
- [x] Identify cultural outliers: games with >50% sales in one region and <10% in each other
- [x] Calculate a **Cultural Specificity Score** for each game
- [x] Visualize temporal shifts and cultural outliers
- [x] Summarize divergence, temporal, and cultural findings

---

## Phase 15: Visualization, Storytelling & Deliverables

> **Note:** The final dashboard should look like dashboards in `02.10/output` and `second_proj/output`. Check dashboard generation scripts (`02.10/dashboard.py`, `second_proj/dashboard.py`) when needed.

- [x] Create polished visualizations: global sales trends, top genres bar chart, regional heatmap, publisher rankings, platform evolution
- [x] Ensure all plots have clear titles, axis labels, legends, and annotations
- [x] Write a **Short Conclusion** summarizing key insights, data wrangling challenges, and how visualization helped
- [x] Build final HTML dashboard (`output/dashboard.html`) modeled after `02.10/output` and `second_proj/output`
- [x] Review the entire Jupyter Notebook for clean code, comments, and explanatory text cells
- [x] Generate the project management **CSV file** with EPICs, User Stories, Features, and Dev Tasks (as specified in the project requirements)
- [x] Perform a final quality review of all deliverables
