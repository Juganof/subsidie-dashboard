# RVO Glass Subsidy Scraper

This project scrapes information about glass options and subsidy amounts from the Dutch Enterprise Agency (RVO) website. It collects data about various types of glass and their corresponding subsidy amounts under the ISDE program (Investeringssubsidie Duurzame Energie).

## Features

- Scrapes glass options from the RVO website
- Extracts detailed information including:
  - Glass type (e.g., Triple glass, HR++ glass)
  - Brand/manufacturer
  - Code (meldcode)
  - Category
  - Housing type
  - U-value
  - Subsidy amounts for different scenarios (single/multiple measures, normal/monument housing)
- Saves data in structured CSV and JSON formats
- Updates the configuration file with the latest subsidy values

## Files

- `scraper.py` - Main scraping script that extracts data from the RVO website
- `update_config.py` - Script to update the configuration file with the latest subsidies
- `config.py` - Configuration file with subsidy specifications

## Requirements

- Python 3.6+
- Required packages: requests, beautifulsoup4, pandas, lxml

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install requests beautifulsoup4 pandas lxml
```

## Usage

### 1. Run the scraper

```bash
python scraper.py
```

This will:
- Scrape the RVO website for glass subsidy information
- Process the data
- Save the results in three files:
  - `rvo_glass_data.csv` - Raw scraped data
  - `rvo_glass_data.json` - Raw data in JSON format
  - `rvo_glass_data_processed.csv` - Structured and cleaned data

### 2. Update the configuration

After running the scraper, you can update the configuration file with the latest subsidy values:

```bash
python update_config.py
```

This will:
- Read the processed data from `rvo_glass_data_processed.csv`
- Parse the current `config.py` file
- Update the subsidy values in the configuration
- Create a backup of the original configuration as `config.py.bak`
- Save the updated configuration to `config.py`

## Data Structure

The processed data includes the following fields:

- `meldcode` - The unique code for the glass option
- `type` - The type/model of the glass
- `merk` - The brand/manufacturer
- `categorie` - The category (e.g., Triple glass, HR++ glass)
- `woningtype` - The housing type (e.g., All homes, Monument only)
- `u_waarde` - The U-value (thermal transmittance)
- `subsidy_2025_single` - Subsidy amount for a single measure from 2025
- `subsidy_2025_multiple` - Subsidy amount when combined with other measures from 2025
- `subsidy_2024_single` - Subsidy amount for a single measure until end of 2024
- `subsidy_2024_multiple` - Subsidy amount when combined with other measures until end of 2024
- `subsidy_2025_monument_single` - Subsidy amount for monuments, single measure from 2025
- `subsidy_2025_monument_multiple` - Subsidy amount for monuments, multiple measures from 2025
- `subsidy_2024_monument_single` - Subsidy amount for monuments, single measure until end of 2024
- `subsidy_2024_monument_multiple` - Subsidy amount for monuments, multiple measures until end of 2024
- `url` - The URL of the glass option on the RVO website

## Notes

- The scraper implements a polite delay between requests to avoid overloading the RVO server.
- The update script creates a backup of the configuration file before making changes.
- Some glass options may not map directly to config entries, in which case they will be ignored.

## Disclaimer

This tool is intended for informational purposes only. Always refer to the official RVO website for the most accurate and up-to-date information about subsidies. 