import csv

queries = [
    {
        "description": "Get all records from fund_data",
        "query": "SELECT * FROM fund_data;",
    },
    {
        "description": "Get all records from fund_data",
        "query": "SELECT * FROM fund_data;",
    },
    {
        "description": "Get all unique fund names",
        "query": "SELECT DISTINCT scheme_name FROM fund_data;",
    },
    {
        "description": "Get the latest price for each fund",
        "query": """
            SELECT scheme_name, sale_price_per_unit
            FROM fund_data
            WHERE (scheme_name, date_valued) IN (
                SELECT scheme_name, MAX(date_valued)
                FROM fund_data
                GROUP BY scheme_name
            );
        """,
    },
    {
        "description": "Get the total sale_price_per_unit for each fund",
        "query": "SELECT scheme_name, SUM(sale_price_per_unit) FROM fund_data GROUP BY scheme_name;",
    },
    {
        "description": "Get the number of records for each fund",
        "query": "SELECT scheme_name, COUNT(*) FROM fund_data GROUP BY scheme_name;",
    },
    {
        "description": "Get the earliest and latest date_valued for each fund",
        "query": "SELECT scheme_name, MIN(date_valued), MAX(date_valued) FROM fund_data GROUP BY scheme_name;",
    },
    {
        "description": "Get the sale_price_per_unit for the latest date_valued for each fund",
        "query": """
        SELECT scheme_name, sale_price_per_unit
        FROM fund_data
        WHERE date_valued = (
            SELECT MAX(date_valued)
            FROM fund_data AS fd
            WHERE fd.scheme_name = fund_data.scheme_name
        );
    """,
    },
    {
        "description": "Get the fund with the highest average sale_price_per_unit for each year",
        "query": """
        SELECT YEAR(date_valued) AS year, scheme_name, AVG(sale_price_per_unit) AS avg_price
        FROM fund_data
        GROUP BY year, scheme_name
        ORDER BY avg_price DESC;
    """,
    },
    {
        "description": "Get the fund with the highest total sale_price_per_unit for each month in 2020",
        "query": """
        SELECT MONTH(date_valued) AS month, scheme_name, SUM(sale_price_per_unit) AS total_price
        FROM fund_data
        WHERE YEAR(date_valued) = 2020
        GROUP BY month, scheme_name
        ORDER BY total_price DESC;
    """,
    },
    {
        "description": "Get the top 3 funds with the highest average sale_price_per_unit for each quarter in 2020",
        "query": """
        SELECT QUARTER(date_valued) AS quarter, scheme_name, AVG(sale_price_per_unit) AS avg_price
        FROM fund_data
        WHERE YEAR(date_valued) = 2020
        GROUP BY quarter, scheme_name
        ORDER BY avg_price DESC
        LIMIT 3;
    """,
    },
    {
        "description": "Get the fund with the highest sale_price_per_unit for the last date_valued of each month in 2020",
        "query": """
        SELECT scheme_name, sale_price_per_unit
        FROM fund_data
        WHERE date_valued IN (
            SELECT MAX(date_valued)
            FROM fund_data
            WHERE YEAR(date_valued) = 2020
            GROUP BY MONTH(date_valued)
        )
        ORDER BY sale_price_per_unit DESC;
    """,
    },
    {
        "description": "Get the fund with the lowest average sale_price_per_unit",
        "query": """
        SELECT scheme_name, AVG(sale_price_per_unit) AS avg_price
        FROM fund_data
        GROUP BY scheme_name
        ORDER BY avg_price ASC
        LIMIT 1;
    """,
    },
    {
        "description": "Get the date with the highest total sale_price_per_unit for all funds",
        "query": """
        SELECT date_valued, SUM(sale_price_per_unit) AS total_price
        FROM fund_data
        GROUP BY date_valued
        ORDER BY total_price DESC
        LIMIT 1;
    """,
    },
    {
        "description": "Get the fund with the most records in the database",
        "query": """
        SELECT scheme_name, COUNT(*) AS count
        FROM fund_data
        GROUP BY scheme_name
        ORDER BY count DESC
        LIMIT 1;
    """,
    },
    {
        "description": "Get the date with the most records in the database",
        "query": """
        SELECT date_valued, COUNT(*) AS count
        FROM fund_data
        GROUP BY date_valued
        ORDER BY count DESC
        LIMIT 1;
    """,
    },
    {
        "description": "Get the fund with the highest sale_price_per_unit on the latest date_valued",
        "query": """
        SELECT scheme_name, sale_price_per_unit
        FROM fund_data
        WHERE date_valued = (
            SELECT MAX(date_valued)
            FROM fund_data
        )
        ORDER BY sale_price_per_unit DESC
        LIMIT 1;
    """,
    },
    {
        "description": "Get the percentage change in average sale_price_per_unit from the previous month for each fund in 2020",
        "query": """
        SELECT scheme_name, MONTH(date_valued) AS month, 
        ((AVG(sale_price_per_unit) - LAG(AVG(sale_price_per_unit)) OVER (PARTITION BY scheme_name ORDER BY month)) / LAG(AVG(sale_price_per_unit)) OVER (PARTITION BY scheme_name ORDER BY month)) * 100 AS pct_change
        FROM fund_data
        WHERE YEAR(date_valued) = 2020
        GROUP BY scheme_name, month;
    """,
    },
    {
        "description": "Get the top 5 funds with the highest average sale_price_per_unit",
        "query": """
        SELECT scheme_name, AVG(sale_price_per_unit) AS avg_price
        FROM fund_data
        GROUP BY scheme_name
        ORDER BY avg_price DESC
        LIMIT 5;
    """,
    },
    {
        "description": "Calculate percentage return of funds in 2020",
        "query": """
            SELECT 
                start_price.scheme_name, 
                ((end_price.sale_price_per_unit - start_price.sale_price_per_unit) / start_price.sale_price_per_unit) * 100 AS percentage_return
            FROM 
                (SELECT scheme_name, sale_price_per_unit
                FROM fund_data
                WHERE scheme_name IN ('Liquid Fund', 'Bond Fund') AND date_valued = (SELECT MIN(date_valued) FROM fund_data WHERE scheme_name = fund_data.scheme_name)
                GROUP BY scheme_name) AS start_price,
                (SELECT scheme_name, sale_price_per_unit
                FROM fund_data
                WHERE scheme_name IN ('Liquid Fund', 'Bond Fund') AND date_valued = (SELECT MAX(date_valued) FROM fund_data WHERE scheme_name = fund_data.scheme_name)
                GROUP BY scheme_name) AS end_price
            WHERE start_price.scheme_name = end_price.scheme_name;
        """,
    },
    {
        "description": "Calculate Sharpe Ratio of Liquid Fund in 2020",
        "query": """
            SELECT 
                scheme_name,
                AVG(daily_return) AS avg_return,
                STDDEV_POP(daily_return) AS std_dev,
                (AVG(daily_return) - 12) / STDDEV_POP(daily_return) AS sharpe_ratio
            FROM 
                (SELECT 
                    scheme_name,
                    ((sale_price_per_unit - LAG(sale_price_per_unit) OVER (PARTITION BY scheme_name ORDER BY date_valued)) / LAG(sale_price_per_unit) OVER (PARTITION BY scheme_name ORDER BY date_valued)) * 100 AS daily_return
                FROM 
                    fund_data
                WHERE 
                    scheme_name = 'Liquid Fund' AND YEAR(date_valued) = 2020) AS daily_returns
            GROUP BY 
                scheme_name;
        """,
    },
    {
        "description": "Get the total number of records in fund_data",
        "query": "SELECT COUNT(*) FROM fund_data;",
    },
    {
        "description": "Get the average sale_price_per_unit for each fund",
        "query": "SELECT scheme_name, AVG(sale_price_per_unit) FROM fund_data GROUP BY scheme_name;",
    },
    {
        "description": "Get all unique fund names",
        "query": "SELECT DISTINCT scheme_name FROM fund_data;",
    },
    {
        "description": "Get the latest price for each fund",
        "query": """
            SELECT scheme_name, sale_price_per_unit
            FROM fund_data
            WHERE (scheme_name, date_valued) IN (
                SELECT scheme_name, MAX(date_valued)
                FROM fund_data
                GROUP BY scheme_name
            );
        """,
    },
    {
        "description": "Calculate percentage return of funds in 2020",
        "query": """
            SELECT 
                start_price.scheme_name, 
                ((end_price.sale_price_per_unit - start_price.sale_price_per_unit) / start_price.sale_price_per_unit) * 100 AS percentage_return
            FROM 
                (SELECT scheme_name, sale_price_per_unit
                FROM fund_data
                WHERE scheme_name IN ('Liquid Fund', 'Bond Fund') AND date_valued = (SELECT MIN(date_valued) FROM fund_data WHERE scheme_name = fund_data.scheme_name)
                GROUP BY scheme_name) AS start_price,
                (SELECT scheme_name, sale_price_per_unit
                FROM fund_data
                WHERE scheme_name IN ('Liquid Fund', 'Bond Fund') AND date_valued = (SELECT MAX(date_valued) FROM fund_data WHERE scheme_name = fund_data.scheme_name)
                GROUP BY scheme_name) AS end_price
            WHERE start_price.scheme_name = end_price.scheme_name;
        """,
    },
    {
        "description": "Calculate Sharpe Ratio of Liquid Fund in 2020",
        "query": """
            SELECT 
                scheme_name,
                AVG(daily_return) AS avg_return,
                STDDEV_POP(daily_return) AS std_dev,
                (AVG(daily_return) - 12) / STDDEV_POP(daily_return) AS sharpe_ratio
            FROM 
                (SELECT 
                    scheme_name,
                    ((sale_price_per_unit - LAG(sale_price_per_unit) OVER (PARTITION BY scheme_name ORDER BY date_valued)) / LAG(sale_price_per_unit) OVER (PARTITION BY scheme_name ORDER BY date_valued)) * 100 AS daily_return
                FROM 
                    fund_data
                WHERE 
                    scheme_name = 'Liquid Fund' AND YEAR(date_valued) = 2020) AS daily_returns
            GROUP BY 
                scheme_name;
        """,
    },
]

with open("queries.csv", "w", newline="") as csvfile:
    fieldnames = ["description", "query"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for query in queries:
        writer.writerow(query)
