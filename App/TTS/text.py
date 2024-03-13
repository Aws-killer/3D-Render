
x={
      "name": "execute_sql",
      "description": "Executes the sql query, the schema of the table is CREATE TABLE fund_data (id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, scheme_id BIGINT UNSIGNED DEFAULT 0, net_asset_value DECIMAL(20, 4), outstanding_number_of_units DECIMAL(20, 4), nav_per_unit DECIMAL(20, 4), sale_price_per_unit DECIMAL(20, 4), repurchase_price_per_unit DECIMAL(20, 4), date_valued DATE, scheme_name VARCHAR(255)); all calculations should end in the current date and nothing more, for the lastest price of any fund use the last recorded price, using  sale_price_per_unit create a sql query to pass to the execute_sql. There is Liquid Fund, Umoja Fund, Bond Fund, Jikimu Fund Wekeza Maisha Fund and Watoto Fund. Make sure that the  syntax is valid!",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "SQL query passed to the "
          }
        },
        "required": ["query"]
      }
    }

#sql query to 