import boto3
import pymysql
import csv
from datetime import datetime

# Configuration
S3_BUCKET_NAME = "s386to98rds"
RDS_HOST = "database-1.us-east-1.rds.amazonaws.com"  # Replace <region> with your RDS region
RDS_USER = "admin"
RDS_PASSWORD = "prathmesh"
RDS_DATABASE = "database-1"  # Replace with your database name
S3_FILE_NAME = "sample_data.csv"  # Replace with the name of the file in S3

# Step 1: Read from S3
def read_from_s3():
    try:
        print("Connecting to S3...")
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_NAME)
        content = response["Body"].read().decode("utf-8")
        data = list(csv.reader(content.splitlines()))
        print(f"Data read from S3: {data}")
        return data
    except Exception as e:
        print(f"Error reading from S3: {e}")
        return []

# Step 2: Write to RDS
def write_to_rds(data):
    try:
        print("Connecting to RDS...")
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DATABASE,
        )
        cursor = connection.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                UserID INT PRIMARY KEY,
                Name VARCHAR(255),
                Email VARCHAR(255),
                Phone VARCHAR(15),
                RegistrationDate DATE
            )
        """)
        print("Table checked/created successfully.")

        # Skip the header row and insert data
        for row in data[1:]:
            user_id = int(row[0])  # Convert UserID to integer
            name = row[1]
            email = row[2]
            phone = row[3]
            registration_date = datetime.strptime(row[4], "%Y-%m-%d").date()  # Convert to DATE

            cursor.execute("""
                INSERT INTO user_data (UserID, Name, Email, Phone, RegistrationDate)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    Name=VALUES(Name),
                    Email=VALUES(Email),
                    Phone=VALUES(Phone),
                    RegistrationDate=VALUES(RegistrationDate)
            """, (user_id, name, email, phone, registration_date))

        connection.commit()
        print("Data written to RDS successfully.")
    except Exception as e:
        print(f"Error writing to RDS: {e}")
    finally:
        if connection:
            connection.close()

# Main script
if __name__ == "__main__":
    # Read data from S3
    s3_data = read_from_s3()

    if s3_data:
        # Write data to RDS
        write_to_rds(s3_data)
    else:
        print("No data to write.")
