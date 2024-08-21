```sql
WITH TopCategories AS (
    SELECT 
        p.category AS category_name,
        SUM(oi.quantity * oi.price_per_unit) AS total_spent
    FROM 
        Orders o
    INNER JOIN 
        Order_Items oi 
        ON oi.order_id = o.order_id
    INNER JOIN 
        Products p 
        ON p.product_id = oi.product_id
    WHERE 
        o.order_date >= DATEADD(YEAR, -1, GETDATE())
    GROUP BY 
        p.category
    ORDER BY 
        total_spent DESC
    LIMIT 5  -- Use LIMIT instead of TOP for databases like PostgreSQL or MySQL
),
CustomerSpending AS (
    SELECT
        c.customer_id, 
        c.customer_name,
        c.email,
        p.category,
        SUM(oi.quantity * oi.price_per_unit) AS total_spent
    FROM 
        Customers c
    INNER JOIN 
        Orders o 
        ON c.customer_id = o.customer_id 
    INNER JOIN 
        Order_Items oi 
        ON oi.order_id = o.order_id 
    INNER JOIN 
        Products p 
        ON p.product_id = oi.product_id
    WHERE 
        o.order_date >= DATEADD(YEAR, -1, GETDATE()) AND
        p.category IN (SELECT category_name FROM TopCategories)
    GROUP BY 
        c.customer_id, c.customer_name, c.email, p.category
),
RankedSpending AS (
    SELECT 
        customer_id, 
        customer_name, 
        email, 
        category, 
        total_spent,
        RANK() OVER (PARTITION BY customer_id ORDER BY total_spent DESC) AS category_rank
    FROM 
        CustomerSpending
)
SELECT 
    customer_id,
    customer_name,
    email,
    SUM(total_spent) AS total_spent,
    MAX(CASE WHEN category_rank = 1 THEN category ELSE NULL END) AS most_purchased_category
FROM 
    RankedSpending
GROUP BY 
    customer_id, customer_name, email
ORDER BY 
    total_spent DESC
LIMIT 5;
```
