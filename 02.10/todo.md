# Data Project – International Customer Satisfaction Analysis

## Description

FastColis is a parcel delivery company operating in several countries (France, Spain, Germany, Morocco, and Canada).

Each local branch regularly conducts customer satisfaction surveys to assess service quality:

- Delivery time
- Interaction with the courier
- Parcel condition
- Customer service availability

However, the survey tools used differ across countries:

- In France, data is stored in an Excel file with ratings out of 5.
- In Spain, the format is JSON and responses use “Bajo / Medio / Alto”.
- In Canada, ratings are out of 10.
- In Morocco, surveys are entered as free text.
- In Germany, products use different codes (e.g., PAK_001 instead of COLIS_STANDARD).

Set up a centralized data platform that can:

- Automatically collect satisfaction surveys from each country.
- Clean and structure the data using a common format.
- Create a global product reference because each country uses its own naming conventions.
- Normalize satisfaction scores (all scales converted to 5).
- Enable AI queries such as:
  - “For France, what is the satisfaction level with after-sales service?”
  - “Which product has the lowest average satisfaction score globally?”

## Examples

- As a Data Engineer, I want to centralize all surveys in a common format to enable global analysis.
- As a Data Analyst, I want to access clean data to calculate average satisfaction by country.
- As a Data Steward, I want to create a single product reference to harmonize product names.

## Work to Do

### Requirements analysis

- [x] Define the business objectives: comparability, quality, and speed of analysis.
- [x] Identify the main constraints (different formats, lack of a common reference, etc.).
- [x] Describe the Product Backlog and Sprint 1 Backlog.
- [ ] Product master data (need it to map data and for other projects)

You can create sample fictitious files and carry out the project!

- [ ] Release 1: Your client wants an overview of customer satisfaction by country and overall satisfaction.
