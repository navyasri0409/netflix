"""
Netflix Movies and TV Shows Data Cleaning, EDA, and Visualization Pipeline
Author: Senior Data Analyst
Description: This script loads the Netflix dataset, performs data quality checks,
             cleans the data, runs comprehensive exploratory data analysis (EDA),
             generates professional visualizations, and saves them to disk.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# DESIGN SYSTEM & COLOR PALETTE CONFIGURATION
# ==========================================
# Set up a premium Netflix-themed palette for all visualizations
NETFLIX_RED = '#E50914'       # Primary accent color
NETFLIX_DARK = '#221F1F'      # Secondary text and dark elements
NETFLIX_LIGHT = '#F5F5F1'     # Background tint for specific charts
NETFLIX_GREY = '#737373'      # Muted gray for grids and sub-elements
NETFLIX_BLACK = '#0f0f0f'     # Deep black for headers

# Set global matplotlib styles
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.labelcolor': NETFLIX_DARK,
    'axes.edgecolor': '#E0E0E0',
    'xtick.color': NETFLIX_DARK,
    'ytick.color': NETFLIX_DARK,
    'text.color': NETFLIX_DARK,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'figure.titlesize': 16,
    'figure.titleweight': 'bold'
})

def main():
    print("=" * 60)
    print("NETFLIX DATA ANALYTICS PIPELINE - STARTING")
    print("=" * 60)
    
    # ------------------------------------------
    # PHASE 1: DATA LOADING & INSPECTION
    # ------------------------------------------
    print("\n--- PHASE 1: DATA LOADING & INSPECTION ---")
    file_path = "netflix_titles.csv"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: {file_path} not found in the current directory.")
        
    df = pd.read_csv(file_path)
    print(f"Dataset successfully loaded. Shape: {df.shape[0]} rows, {df.shape[1]} columns.\n")
    
    print("1. First 5 Rows (df.head()):")
    print(df.head())
    print("\n2. Last 5 Rows (df.tail()):")
    print(df.tail())
    print("\n3. Random Sample of 3 Rows (df.sample(3)):")
    print(df.sample(3, random_state=42))
    
    print("\n4. Columns in Dataset:")
    print(df.columns.tolist())
    
    print("\n5. Dataset Info Summary (df.info()):")
    df.info()
    
    print("\n6. Descriptive Statistics (df.describe() - Object columns):")
    print(df.describe(include=[object]))
    print("\n7. Descriptive Statistics (df.describe() - Numerical columns):")
    print(df.describe())
    
    print("\n8. Column Data Types (df.dtypes):")
    print(df.dtypes)
    
    # Column descriptions dictionary
    column_descriptions = {
        "show_id": "Unique identifier for each movie/TV show.",
        "type": "General category of content (Movie or TV Show).",
        "title": "Title of the movie or TV show.",
        "director": "Director of the movie/TV show. Contains multiple values separated by commas.",
        "cast": "List of actors appearing in the show, separated by commas.",
        "country": "Country or countries where the show was produced, separated by commas.",
        "date_added": "The date the show was added to Netflix.",
        "release_year": "The original release year of the show.",
        "rating": "The content rating of the show (e.g., TV-MA, PG-13, R, TV-14).",
        "duration": "Duration of the show. Movies in minutes (e.g., '90 min'), TV shows in seasons (e.g., '2 Seasons').",
        "listed_in": "Genres the show is classified under, separated by commas.",
        "description": "A brief summary of the show's plot."
    }
    
    print("\n9. Column Descriptions and Purpose:")
    for col, desc in column_descriptions.items():
        print(f" - *{col}*: {desc}")

    # ------------------------------------------
    # PHASE 2: DATA QUALITY ASSESSMENT
    # ------------------------------------------
    print("\n--- PHASE 2: DATA QUALITY ASSESSMENT ---")
    
    # Missing values check
    missing_counts = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df)) * 100
    dq_report = pd.DataFrame({
        'Missing Values': missing_counts,
        'Percentage (%)': missing_pct,
        'Data Type': df.dtypes
    })
    print("1. Data Quality and Missing Values Summary:")
    print(dq_report.to_string())
    
    # Duplicates check
    duplicate_rows = df.duplicated().sum()
    print(f"\n2. Duplicate Records Count: {duplicate_rows}")
    
    # Inconsistent text check
    print("\n3. Unique Values in Type Column:")
    print(df['type'].unique())
    
    # Mixed-format and misaligned columns check
    # Check for non-standard duration units or ratings that look like durations
    duration_in_ratings = df[df['rating'].astype(str).str.contains('min|Season', na=False)]
    if not duration_in_ratings.empty:
        print("\n4. Alert: Found values in 'rating' column that look like durations (misaligned rows):")
        print(duration_in_ratings[['title', 'rating', 'duration']])
        
    print("\n5. Possible Reasons for Missing Data:")
    print(" - *director*: High missingness (~30%) because many TV shows do not list an overall director,")
    print("               or this information was not aggregated during scraping/collection.")
    print(" - *cast*: Missing (~9.3%) because some documentaries, reality shows, or news programs do not have a standard cast.")
    print(" - *country*: Missing (~9.4%) because production countries may not be listed or are obscure/unconfirmed.")
    print(" - *date_added*: Missing (~0.1%) because historical titles on Netflix may have lost their precise addition dates.")
    print(" - *rating* & *duration*: Extremely minor missingness (~0.04%), typically caused by parser shift or manual data entry errors.")

    # ------------------------------------------
    # PHASE 3: DATA CLEANING
    # ------------------------------------------
    print("\n--- PHASE 3: DATA CLEANING ---")
    df_clean = df.copy()
    
    # 1. Heatmap representation: Save missing value heatmap before cleaning
    os.makedirs('plots', exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Values Heatmap (Before Cleaning)", pad=20)
    plt.tight_layout()
    plt.savefig('plots/plot_10_missing_heatmap_before.png', dpi=300)
    plt.close()
    print("Saved 'plot_10_missing_heatmap_before.png' to plots/ directory.")
    
    # 2. Fix shifted Louis C.K. rows programmatically
    # Identify rows where duration is NaN and rating contains 'min'
    shifted_mask = df_clean['duration'].isnull() & df_clean['rating'].astype(str).str.contains('min')
    if shifted_mask.any():
        print(f"Fixing {shifted_mask.sum()} misaligned Louis C.K. rows...")
        df_clean.loc[shifted_mask, 'duration'] = df_clean.loc[shifted_mask, 'rating']
        df_clean.loc[shifted_mask, 'rating'] = 'UR'  # Set rating to 'UR' (Unrated)
        
    # 3. Standardize text columns (strip whitespaces)
    string_cols = ['type', 'title', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']
    for col in string_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            
    # 4. Handle Missing Values column by column
    print("Imputing missing values...")
    # Replace the 'nan' string (produced by casting to str and stripping) back to actual NaNs or directly fill them
    df_clean['director'] = df_clean['director'].replace('nan', 'Unknown Director')
    df_clean['cast'] = df_clean['cast'].replace('nan', 'Unknown Cast')
    df_clean['country'] = df_clean['country'].replace('nan', 'Unknown Country')
    df_clean['rating'] = df_clean['rating'].replace('nan', 'UR')
    
    # Check if there are other nulls in rating (e.g. from the original dataset)
    df_clean['rating'] = df_clean['rating'].fillna('UR')
    
    # For date_added, drop the rows with missing values (10 rows)
    # Check for both actual NaNs and the string 'nan'
    df_clean = df_clean[df_clean['date_added'] != 'nan']
    df_clean = df_clean.dropna(subset=['date_added'])
    print(f"Dropped rows with missing date_added. Shape is now: {df_clean.shape}")
    
    # 5. Remove duplicates
    initial_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    print(f"Removed duplicates. Rows removed: {initial_rows - len(df_clean)}")
    
    # 6. Convert date_added to datetime and extract time components
    df_clean['date_added'] = pd.to_datetime(df_clean['date_added'].str.strip(), errors='coerce')
    df_clean = df_clean.dropna(subset=['date_added'])
    df_clean['year_added'] = df_clean['date_added'].dt.year.astype(int)
    df_clean['month_added'] = df_clean['date_added'].dt.month_name()
    df_clean['month_num_added'] = df_clean['date_added'].dt.month.astype(int)
    
    # 7. Clean duration column and split into duration_num and duration_type
    print("Splitting duration into duration_num and duration_type...")
    # Extract number (e.g. "90 min" -> 90)
    df_clean['duration_num'] = df_clean['duration'].apply(lambda x: float(str(x).split(' ')[0]) if pd.notnull(x) and str(x) != 'nan' else 0.0)
    
    # Extract unit and standardize Seasons/Season -> Season
    df_clean['duration_type'] = df_clean['duration'].apply(
        lambda x: 'Season' if 'Season' in str(x) else ('min' if 'min' in str(x) else 'Unknown')
    )
    
    # 8. Verify Data Types and Null Counts after cleaning
    print("\nVerification of Dataset After Cleaning:")
    print(df_clean.info())
    print("\nMissing values count after cleaning:")
    print(df_clean.isnull().sum())
    
    # Export cleaned dataset
    df_clean.to_csv("netflix_cleaned.csv", index=False)
    print("\nCleaned dataset exported to 'netflix_cleaned.csv'.")

    # ------------------------------------------
    # PHASE 4: EXPLORATORY DATA ANALYSIS (EDA)
    # ------------------------------------------
    print("\n--- PHASE 4: EXPLORATORY DATA ANALYSIS (EDA) ---")
    
    # Create an analysis summary report string to write to disk
    eda_report = []
    
    def log_and_print(section_title, objective, code_desc, output_str, business_insight):
        formatted = f"=== {section_title} ===\n" \
                    f"Objective: {objective}\n" \
                    f"Code: {code_desc}\n" \
                    f"Output:\n{output_str}\n" \
                    f"Business Insight:\n{business_insight}\n" \
                    f"{'-'*50}\n"
        print(formatted)
        eda_report.append(formatted)

    # 1. Movies vs TV Shows Count
    m_vs_tv = df_clean['type'].value_counts()
    log_and_print(
        "1. Movies vs TV Shows count",
        "Understand the proportion of movies compared to TV shows on Netflix.",
        "df_clean['type'].value_counts()",
        m_vs_tv.to_string(),
        "Netflix's library is heavily dominated by Movies, which account for roughly 70% of the content. "
        "However, TV shows are highly critical for user engagement and retention due to their longer viewing hours."
    )

    # 2. Content added over the years
    content_added_years = df_clean['year_added'].value_counts().sort_index()
    log_and_print(
        "2. Content added over the years",
        "Identify when Netflix began rapidly expanding its content library.",
        "df_clean['year_added'].value_counts().sort_index()",
        content_added_years.to_string(),
        "Library expansion started growing exponentially in 2015, peaking around 2019. "
        "The subsequent slight dip in additions in 2020-2021 was likely impacted by production shutdowns "
        "and delays caused by the COVID-19 pandemic, alongside Netflix focusing on quality/original productions."
    )

    # 3. Top countries producing Netflix content (Exploded for accurate counts)
    exploded_countries = df_clean['country'].str.split(', ').explode()
    # Remove 'Unknown Country' for finding top producing countries
    top_countries = exploded_countries[exploded_countries != 'Unknown Country'].value_counts().head(10)
    log_and_print(
        "3. Top countries producing Netflix content (Exploded)",
        "Determine the key production hubs for Netflix content.",
        "df_clean['country'].str.split(', ').explode().value_counts().head(10)",
        top_countries.to_string(),
        "The United States remains the largest producer of Netflix content, followed by India and the United Kingdom. "
        "This highlights Netflix's strategic investments in Bollywood and British productions to capture local and global viewers."
    )

    # 4. Most common ratings
    ratings_count = df_clean['rating'].value_counts()
    log_and_print(
        "4. Most common ratings",
        "Analyze the target audience demographics based on content ratings.",
        "df_clean['rating'].value_counts()",
        ratings_count.to_string(),
        "TV-MA (Mature Audience) and TV-14 (Parents Strongly Cautioned) are the most dominant ratings. "
        "This indicates that Netflix’s primary target audience consists of mature teens and adults, "
        "which aligns with its marketing strategy of edgy, high-production dramas and series."
    )

    # 5. Most common genres (Exploded for accurate counts)
    exploded_genres = df_clean['listed_in'].str.split(', ').explode()
    top_genres = exploded_genres.value_counts().head(10)
    log_and_print(
        "5. Most common genres (Exploded)",
        "Identify which genres are most heavily stocked on the platform.",
        "df_clean['listed_in'].str.split(', ').explode().value_counts().head(10)",
        top_genres.to_string(),
        "International Movies, Dramas, and Comedies are the most common genres. "
        "The high prevalence of 'International Movies' reflects Netflix’s localized content strategy, "
        "enabling regional films to reach a global subscriber base."
    )

    # 6. Distribution of movie durations
    movie_durations = df_clean[df_clean['type'] == 'Movie']['duration_num']
    movie_dur_desc = movie_durations.describe()
    log_and_print(
        "6. Distribution of movie durations",
        "Examine the standard runtime of movies on the platform.",
        "df_clean[df_clean['type'] == 'Movie']['duration_num'].describe()",
        movie_dur_desc.to_string(),
        "The average runtime of a Netflix movie is approximately 99.6 minutes (1h 40m). "
        "The standard deviation is ~28 minutes, indicating a wide variety of film lengths, "
        "ranging from short films (minimum of 3 minutes) to epic movies (maximum of 312 minutes)."
    )

    # 7. Distribution of TV show seasons
    tv_seasons = df_clean[df_clean['type'] == 'TV Show']['duration_num']
    tv_seasons_pct = tv_seasons.value_counts(normalize=True).head(5) * 100
    log_and_print(
        "7. Distribution of TV show seasons",
        "Understand the longevity and release patterns of TV shows.",
        "df_clean[df_clean['type'] == 'TV Show']['duration_num'].value_counts(normalize=True).head(5) * 100",
        tv_seasons_pct.to_string(),
        "Nearly 67% of all TV shows on Netflix end after 1 Season, and only ~14% reach a 2nd Season. "
        "Netflix frequently cancels underperforming shows early to optimize budget allocations, "
        "relying heavily on fresh Season 1 launches to drive user sign-ups."
    )

    # 8. Top directors by number of titles (Exploded, excluding 'Unknown Director')
    exploded_directors = df_clean['director'].str.split(', ').explode()
    top_directors = exploded_directors[exploded_directors != 'Unknown Director'].value_counts().head(10)
    log_and_print(
        "8. Top directors by number of titles",
        "Identify the most prolific directors contributing to the library.",
        "df_clean['director'].str.split(', ').explode().value_counts().head(10)",
        top_directors.to_string(),
        "Rajiv Chilaka (known for Indian animated children's shows), Jan Suter, and Raul Campos top the list. "
        "The list is dominated by international directors, showing Netflix's reliance on specific content creators for volume."
    )

    # 9. Top actors appearing in Netflix content (Exploded, excluding 'Unknown Cast')
    exploded_cast = df_clean['cast'].str.split(', ').explode()
    top_cast = exploded_cast[exploded_cast != 'Unknown Cast'].value_counts().head(10)
    log_and_print(
        "9. Top actors appearing in Netflix content",
        "Identify actors with the highest presence on the platform.",
        "df_clean['cast'].str.split(', ').explode().value_counts().head(10)",
        top_cast.to_string(),
        "Anupam Kher, Shah Rukh Khan, and Naseeruddin Shah (all veteran Indian actors) are the most frequent stars. "
        "This underscores the vastness of the Indian film library acquired by Netflix to engage its massive South Asian audience."
    )

    # 10. Content growth trend over time (Cumulative)
    # Group by year_added and count, then take cumulative sum
    growth_df = df_clean.groupby(['year_added', 'type']).size().unstack(fill_value=0)
    growth_cumulative = growth_df.cumsum()
    log_and_print(
        "10. Content growth trend over time (Cumulative)",
        "Track the historical size growth of Netflix's catalog.",
        "df_clean.groupby(['year_added', 'type']).size().unstack(fill_value=0).cumsum()",
        growth_cumulative.tail(5).to_string(),
        "The cumulative volume shows that the platform's library grew aggressively between 2016 and 2019. "
        "The rate of growth has slightly flattened recently, indicating a transition from aggressive acquisition to selective content development."
    )

    # 11. Content added by month
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    content_added_month = df_clean['month_added'].value_counts().reindex(month_order)
    log_and_print(
        "11. Content added by month",
        "Analyze whether there is seasonality in content uploads.",
        "df_clean['month_added'].value_counts().reindex(month_order)",
        content_added_month.to_string(),
        "Content additions are relatively stable across the months, but peak in July, December, and January. "
        "This corresponds with holiday seasons when viewership is at its highest, optimizing subscriber retention."
    )

    # 12. Release year distribution
    release_years_desc = df_clean['release_year'].describe()
    log_and_print(
        "12. Release year distribution",
        "Observe the age of content available in the Netflix library.",
        "df_clean['release_year'].describe()",
        release_years_desc.to_string(),
        "The median release year is 2017, meaning half of the library consists of very recent releases. "
        "However, Netflix also preserves vintage titles, with the oldest film in the dataset dating back to 1925."
    )

    # 13. Movies released per year (top 5 years)
    movies_released_yr = df_clean[df_clean['type'] == 'Movie']['release_year'].value_counts().sort_index().tail(10)
    log_and_print(
        "13. Movies released per year (Recent 10 years)",
        "Track the annual releases of movies over the last decade.",
        "df_clean[df_clean['type'] == 'Movie']['release_year'].value_counts().sort_index().tail(10)",
        movies_released_yr.to_string(),
        "Movie releases peaked in 2017-2018 with over 700 movies each year. "
        "The sharp decline in newer movies after 2018 reflects Netflix's push toward creating its own TV shows/limited series."
    )

    # 14. TV shows released per year (top 5 years)
    tv_released_yr = df_clean[df_clean['type'] == 'TV Show']['release_year'].value_counts().sort_index().tail(10)
    log_and_print(
        "14. TV shows released per year (Recent 10 years)",
        "Track the annual releases of TV shows over the last decade.",
        "df_clean[df_clean['type'] == 'TV Show']['release_year'].value_counts().sort_index().tail(10)",
        tv_released_yr.to_string(),
        "TV Show releases peaked in 2020. Unlike movies, TV show releases remained exceptionally strong "
        "throughout 2020 and 2021, proving Netflix's commitment to episodic streaming content over standalone films."
    )

    # Save the report to disk
    with open("eda_report.txt", "w", encoding="utf-8") as f:
        f.writelines(eda_report)
    print("Saved 'eda_report.txt' summary to disk.")

    # ------------------------------------------
    # PHASE 5: DATA VISUALIZATION
    # ------------------------------------------
    print("\n--- PHASE 5: DATA VISUALIZATION ---")
    
    # 1. Bar Chart: Movies vs TV Shows
    plt.figure(figsize=(7, 5))
    ax = sns.countplot(data=df_clean, x='type', palette=[NETFLIX_RED, NETFLIX_DARK], hue='type', legend=False)
    plt.title("Volume of Movies vs TV Shows", pad=15)
    plt.xlabel("Content Type")
    plt.ylabel("Count")
    # Annotate bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}\n({p.get_height()/len(df_clean)*100:.1f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height() - 500), 
                    ha='center', va='center', color='white', fontweight='bold', xytext=(0, 0), textcoords='offset points')
    plt.tight_layout()
    plt.savefig('plots/plot_1_movies_vs_tvshows.png', dpi=300)
    plt.close()

    # 2. Horizontal Bar Chart: Top 10 Countries
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_countries.values, y=top_countries.index, palette="Reds_r", hue=top_countries.index, legend=False)
    plt.title("Top 10 Countries Producing Netflix Content", pad=15)
    plt.xlabel("Number of Titles (Exploded)")
    plt.ylabel("Country")
    for i, v in enumerate(top_countries.values):
        plt.text(v + 50, i, f'{v}', va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('plots/plot_2_top_countries.png', dpi=300)
    plt.close()

    # 3. Bar Chart: Top Genres
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_genres.values, y=top_genres.index, palette="Oranges_r", hue=top_genres.index, legend=False)
    plt.title("Top 10 Genres on Netflix", pad=15)
    plt.xlabel("Number of Titles (Exploded)")
    plt.ylabel("Genre")
    for i, v in enumerate(top_genres.values):
        plt.text(v + 50, i, f'{v}', va='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig('plots/plot_3_top_genres.png', dpi=300)
    plt.close()

    # 4. Pie Chart: Content Type Distribution (Donut style)
    plt.figure(figsize=(6, 6))
    colors = [NETFLIX_RED, NETFLIX_DARK]
    plt.pie(m_vs_tv.values, labels=m_vs_tv.index, colors=colors, autopct='%1.1f%%', 
            startangle=90, pctdistance=0.75, textprops={'fontweight': 'bold', 'fontsize': 12})
    # Add center circle to make it a donut chart
    centre_circle = plt.Circle((0,0), 0.55, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title("Content Type Distribution (Donut Chart)", pad=15)
    plt.tight_layout()
    plt.savefig('plots/plot_4_content_type_donut.png', dpi=300)
    plt.close()

    # 5. Histogram: Movie Duration Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(movie_durations, bins=30, kde=True, color=NETFLIX_RED, edgecolor='white')
    plt.title("Distribution of Movie Durations", pad=15)
    plt.xlabel("Duration (minutes)")
    plt.ylabel("Density / Count")
    # Draw mean and median lines
    plt.axvline(movie_durations.mean(), color='blue', linestyle='--', linewidth=1.5, label=f'Mean: {movie_durations.mean():.1f} min')
    plt.axvline(movie_durations.median(), color='green', linestyle='-', linewidth=1.5, label=f'Median: {movie_durations.median():.0f} min')
    plt.legend()
    plt.tight_layout()
    plt.savefig('plots/plot_5_movie_duration_dist.png', dpi=300)
    plt.close()

    # 6. Histogram: Release Year Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df_clean, x='release_year', bins=35, kde=False, color=NETFLIX_DARK, edgecolor='white')
    plt.title("Distribution of Content Release Years", pad=15)
    plt.xlabel("Original Release Year")
    plt.ylabel("Count")
    plt.xlim(1940, 2022)  # Focus on modern content but show scale
    plt.tight_layout()
    plt.savefig('plots/plot_6_release_year_dist.png', dpi=300)
    plt.close()

    # 7. Count Plot: Ratings Distribution
    plt.figure(figsize=(12, 6))
    order_ratings = df_clean['rating'].value_counts().index
    sns.countplot(data=df_clean, x='rating', order=order_ratings, palette="coolwarm", hue='rating', legend=False)
    plt.title("Distribution of Content Ratings", pad=15)
    plt.xlabel("Rating Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/plot_7_ratings_distribution.png', dpi=300)
    plt.close()

    # 8. Line Chart: Netflix Content Growth Over Time
    plt.figure(figsize=(10, 6))
    plt.plot(growth_cumulative.index, growth_cumulative['Movie'], label='Movies', color=NETFLIX_RED, linewidth=2.5, marker='o')
    plt.plot(growth_cumulative.index, growth_cumulative['TV Show'], label='TV Shows', color=NETFLIX_DARK, linewidth=2.5, marker='s')
    plt.title("Cumulative Netflix Content Growth Over Time", pad=15)
    plt.xlabel("Year Added")
    plt.ylabel("Total Titles in Catalog (Cumulative)")
    plt.xlim(2008, 2021)
    plt.legend()
    plt.tight_layout()
    plt.savefig('plots/plot_8_content_growth_over_time.png', dpi=300)
    plt.close()

    # 9. Line Chart: Content Added by Year
    plt.figure(figsize=(10, 6))
    plt.plot(growth_df.index, growth_df['Movie'], label='Movies', color=NETFLIX_RED, linewidth=2, marker='o', linestyle='--')
    plt.plot(growth_df.index, growth_df['TV Show'], label='TV Shows', color=NETFLIX_DARK, linewidth=2, marker='s', linestyle=':')
    plt.title("Content Additions per Year", pad=15)
    plt.xlabel("Year Added")
    plt.ylabel("Number of Additions")
    plt.xlim(2008, 2021)
    plt.legend()
    plt.tight_layout()
    plt.savefig('plots/plot_9_content_added_per_year.png', dpi=300)
    plt.close()

    # 10. Heatmap: Missing Values after cleaning (as verification)
    plt.figure(figsize=(10, 6))
    sns.heatmap(df_clean.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Values Heatmap (After Cleaning)", pad=20)
    plt.tight_layout()
    plt.savefig('plots/plot_10_missing_heatmap_after.png', dpi=300)
    plt.close()

    # 11. Correlation Heatmap
    # To compute correlation, let's select numeric columns: release_year, year_added, duration_num (movies only), duration_num (tv shows only)
    # We will build a subset for Movies, and compute correlations between release_year, year_added, and duration_num
    movie_subset = df_clean[df_clean['type'] == 'Movie'][['release_year', 'year_added', 'duration_num']]
    # Rename for readability in plot
    movie_subset.columns = ['Release Year', 'Year Added', 'Movie Duration (min)']
    corr_matrix = movie_subset.corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', vmin=-1, vmax=1, fmt=".3f", linewidths=.5)
    plt.title("Correlation Matrix (Netflix Movies)", pad=15)
    plt.tight_layout()
    plt.savefig('plots/plot_11_correlation_heatmap.png', dpi=300)
    plt.close()

    # 12. Monthly Content Addition Trend
    plt.figure(figsize=(10, 6))
    sns.barplot(x=content_added_month.index, y=content_added_month.values, color=NETFLIX_RED)
    plt.title("Monthly Content Addition Trend (Seasonality)", pad=15)
    plt.xlabel("Month")
    plt.ylabel("Number of Titles Added")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/plot_12_monthly_additions.png', dpi=300)
    plt.close()

    print("All 12 visualizations successfully generated and saved to the 'plots/' folder.")
    print("=" * 60)
    print("NETFLIX DATA ANALYTICS PIPELINE - COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
