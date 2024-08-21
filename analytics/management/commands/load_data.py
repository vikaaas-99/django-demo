import os
import warnings
import random
import pandas as pd
from django.core.management.base import BaseCommand

from analytics.models import ProductData

warnings.filterwarnings("ignore")


class Command(BaseCommand):
    """
    Management command to load product data into the database.

    This command allows users to either provide a CSV file with product data or
    generate random product data. The data is then cleaned and saved to the database.
    """
    help = "Generate random product data or use provided CSV file and save to the database"

    def handle(self, *args, **kwargs):
        """
        Handle the command execution.

        Prompts the user to choose between loading data from a CSV file or generating random data.
        The selected option is then processed accordingly.
        """
        self.stdout.write("Choose an option:")
        self.stdout.write("1. Provide a CSV file")
        self.stdout.write("2. Generate random data and save to the database")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            csv_path = input("Enter the path to the CSV file: ")
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)

                # Checking if the CSV file has the required columns
                if not all(col in df.columns for col in ["product_id", "product_name", "category", "price", "quantity_sold", "rating", "review_count"]):
                    self.stdout.write(self.style.ERROR("CSV file must have columns: `product_id`, `product_name`, `category`, `price`, `quantity_sold`, `rating`, `review_count`"))
                    return
                df = self.clean_data(df)  # Clean the data before saving to the database
                self.save_to_database(df)
                self.stdout.write(self.style.SUCCESS(f"Data from `{csv_path}` saved to the database"))
            else:
                self.stdout.write(self.style.ERROR(f"File `{csv_path}` does not exist"))
        elif choice == "2":
            self.generate_random_data()
        else:
            self.stdout.write(self.style.ERROR("Invalid choice. Please run the command again and choose either 1 or 2."))

    def generate_random_data(self):
        """
        Generate random product data and save it to the database.

        Creates 100 random product entries across different categories and
        saves them to the database.
        """
        categories = ["Electronics", "Books", "Clothing", "Toys", "Home Appliances"]
        products = {
            "Electronics": ["Phone", "Laptop", "Tablet", "Headphones", "Smartwatch"],
            "Books": ["Fiction", "Non-Fiction", "Comics", "Biography", "Mystery"],
            "Clothing": ["T-shirt", "Jeans", "Jacket", "Shirt", "Dress"],
            "Toys": ["Action Figure", "Puzzle", "Board Game", "Doll", "RC Car"],
            "Home Appliances": ["Blender", "Microwave", "Toaster", "Refrigerator", "Washing Machine"]
        }

        data = []

        # Generate 100 rows of random data
        for i in range(1, 101):
            category = random.choice(categories)
            product_name = random.choice(products[category])
            price = round(random.uniform(10, 1000), 2)
            quantity_sold = random.randint(1, 500)
            rating = round(random.uniform(1, 5), 1)
            review_count = random.randint(1, 1000)
            data.append({
                "product_id": i,
                "product_name": product_name,
                "category": category,
                "price": price,
                "quantity_sold": quantity_sold,
                "rating": rating,
                "review_count": review_count
            })

        df = pd.DataFrame(data)
        self.save_to_database(df)
        self.stdout.write(self.style.SUCCESS(f"Random product data generated and saved to the database!"))

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the provided DataFrame by handling missing values and converting data types.

        - Converts price, quantity_sold, and rating columns to numeric types.
        - Fills missing prices and quantities with the median value.
        - Fills missing ratings with the average rating of the corresponding category.
        - Drops any rows with remaining missing values.

        Args:
            df (pd.DataFrame): The DataFrame to clean.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        # Converting columns to numeric
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["quantity_sold"] = pd.to_numeric(df["quantity_sold"], errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

        # Handling missing values
        df["price"].fillna(df["price"].median(), inplace=True)
        df["quantity_sold"].fillna(df["quantity_sold"].median(), inplace=True)

        # Replacing missing ratings with the average rating of the corresponding category
        df["rating"] = df.groupby("category")["rating"].transform(lambda x: x.fillna(x.mean()))

        df = df.dropna(subset=["price", "quantity_sold", "rating"])
        return df

    def save_to_database(self, df: pd.DataFrame):
        """
        Save the product data from the DataFrame to the database.

        Clears any existing ProductData entries before saving the new data.

        Args:
            df (pd.DataFrame): The DataFrame containing the product data to save.
        """
        # Clearing existing data, if any
        ProductData.objects.all().delete()

        for record in df.to_dict("records"):
            ProductData.objects.create(
                product_id=record["product_id"],
                product_name=record["product_name"],
                category=record["category"],
                price=record["price"],
                quantity_sold=record["quantity_sold"],
                rating=record["rating"],
                review_count=record["review_count"]
            )
