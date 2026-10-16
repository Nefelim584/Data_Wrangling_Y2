# TODO — Exploring Global Video Game Sales

> Master task list derived from [Proj.md](file:///Users/nefelim584/PycharmProjects/Data_Wrangling/Fin_project/Proj.md)

---

## Phase 1: Project Setup & Dataset Acquisition

- [ ] Create the project directory structure and initialize the Jupyter Notebook
- [ ] Locate or download the global video game sales dataset (e.g., `vgsales.csv`)
- [ ] Set up a Python virtual environment and install required libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`)
- [ ] Add introductory markdown cells to the notebook explaining the project goal
- [ ] Verify the dataset file is accessible and readable from the notebook

---

## Phase 2: Data Loading & Initial Inspection

- [ ] Load the dataset into a Pandas DataFrame
- [ ] Display the first/last rows and check `.shape`, `.info()`, `.dtypes`
- [ ] Examine column names and understand what each column represents
- [ ] Generate a quick summary with `.describe()` for numerical columns
- [ ] Document initial observations in a markdown cell

---

## Phase 3: Data Cleaning — Missing & Inconsistent Values

- [ ] Identify missing values per column using `.isnull().sum()` and visualize them
- [ ] Investigate patterns behind the missing data (MCAR / MAR / MNAR)
- [ ] Decide on a strategy per column: impute, drop, or leave as-is
- [ ] Apply the chosen strategy and verify no unintended data loss occurred
- [ ] Check for inconsistent values (e.g., typos in platform/genre/publisher names)
- [ ] Standardize any inconsistent categorical values
- [ ] Document all cleaning decisions and rationale in markdown cells

---

## Phase 4: Data Type Correction & Duplicate Removal

- [ ] Convert columns to appropriate data types (e.g., `Year` to integer/datetime)
- [ ] Ensure sales columns are float/numeric
- [ ] Ensure categorical columns (`Genre`, `Platform`, `Publisher`) are of type `category` or clean strings
- [ ] Check for duplicate rows using `.duplicated()`
- [ ] Remove confirmed duplicates and log how many were removed
- [ ] Perform a final sanity check on the cleaned DataFrame

---

## Phase 5: Descriptive Statistics & Top-Selling Games

- [ ] Compute key descriptive statistics for all numerical variables (mean, median, std, min, max)
- [ ] Identify the top 10 best-selling games globally and display them in a table
- [ ] Analyze the distribution of global sales (skewness, outliers)
- [ ] Summarize notable patterns (e.g., highly skewed sales, dominant outliers)
- [ ] Add markdown commentary interpreting the statistics

---

## Phase 6: Trends Over Time

- [ ] Analyze the number of games released per year and plot the trend
- [ ] Plot global sales aggregated by year (line chart)
- [ ] Determine whether sales are increasing, decreasing, or cyclical
- [ ] Identify peak years and correlate them with major industry events (console launches, etc.)
- [ ] Write insights on temporal trends in a markdown cell

---

## Phase 7: Genre Analysis

- [ ] Count games per genre and rank genres by frequency
- [ ] Calculate total and average global sales per genre
- [ ] Visualize genre distribution (bar chart of game count and sales)
- [ ] Identify which genres are most common vs. which generate the most revenue
- [ ] Summarize genre-level insights

---

## Phase 8: Platform Analysis

- [ ] Rank platforms by number of games released and total sales
- [ ] Visualize the most popular platforms (bar charts)
- [ ] Analyze how platform popularity has changed over time (line/area chart)
- [ ] Identify platform lifecycles (rise, peak, decline)
- [ ] Correlate platform trends with console generations
- [ ] Document platform insights

---

## Phase 9: Regional Sales Analysis

- [ ] Compare total sales across NA, EU, JP, and Other regions
- [ ] Calculate regional sales proportions per genre
- [ ] Identify genres that dominate in one region but not others
- [ ] Visualize regional preferences (grouped bar charts or heatmap)
- [ ] Highlight notable regional differences in a markdown cell

---

## Phase 10: Publisher Insights

- [ ] Identify the top 10 publishers by total global sales
- [ ] Visualize publisher rankings (horizontal bar chart)
- [ ] Analyze genre distribution per top publisher
- [ ] Determine if any publisher dominates specific genres ("hit publisher")
- [ ] Summarize publisher-level findings

---

## Phase 11: Market Dominance — Genre Market Share & Publisher Metrics

- [ ] Calculate each publisher's market share within each genre (`publisher genre sales / total genre sales`)
- [ ] Flag publishers as **Genre Leaders** where market share exceeds 30%
- [ ] Compute **Genre Diversity Score** per publisher (number of distinct genres)
- [ ] Compute **Regional Consistency Score** per publisher (std dev of regional sales proportions)
- [ ] Compute **Hit Rate** per publisher (% of games selling above the genre median)
- [ ] Compile all metrics into a single publisher metrics DataFrame

---

## Phase 12: Market Power Index & Publisher Archetypes

- [ ] Design a custom formula combining Genre Diversity, Regional Consistency, and Hit Rate
- [ ] Calculate the **Market Power Index** for every publisher
- [ ] Rank publishers by the Market Power Index
- [ ] Classify publishers into archetypes: **Genre Specialists** vs. **Diversified Giants**
- [ ] Visualize the Market Power Index and archetypes (scatter plot or ranked bar chart)
- [ ] Document the formula, rankings, and archetype definitions

---

## Phase 13: Regional Preference Divergence — Divergence & Affinity Scores

- [ ] Normalize each region's sales as a proportion of each game's total sales
- [ ] Compare each game's regional proportions with the global average proportions
- [ ] Implement a custom divergence function (coefficient of variation or entropy-based)
- [ ] Calculate **Regional Divergence Score** for each game
- [ ] For each genre, compute regional sales distribution and compare to the overall distribution
- [ ] Identify **over-indexed** and **under-indexed** genre-region combinations
- [ ] Create a **Genre-Region Affinity Score** table/heatmap

---

## Phase 14: Temporal Preference Shifts & Cultural Outliers

- [ ] Group data by year and region; determine each region's favorite genre per year
- [ ] Track how regional genre preferences have converged or diverged over time
- [ ] Implement and apply a custom **Preference Stability Index** for each region
- [ ] Identify cultural outliers: games with >50% sales in one region and <10% in each other
- [ ] Calculate a **Cultural Specificity Score** for each game
- [ ] Visualize temporal shifts and cultural outliers
- [ ] Summarize divergence, temporal, and cultural findings

---

## Phase 15: Visualization, Storytelling & Deliverables

- [ ] Create polished visualizations: global sales trends, top genres bar chart, regional heatmap, publisher rankings, platform evolution
- [ ] Ensure all plots have clear titles, axis labels, legends, and annotations
- [ ] Write a **Short Conclusion** summarizing key insights, data wrangling challenges, and how visualization helped
- [ ] Review the entire Jupyter Notebook for clean code, comments, and explanatory text cells
- [ ] Generate the project management **CSV file** with EPICs, User Stories, Features, and Dev Tasks (as specified in the project requirements)
- [ ] Perform a final quality review of all deliverables
