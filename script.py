import boto3
import pymysql
import csv
import logging
from datetime import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration (use environment variables for sensitive data)
import os
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "s386to98rds")
S3_FILE_NAME = os.getenv("S3_FILE_NAME", "sample_data.csv")
RDS_HOST = os.getenv("RDS_HOST", "database-2.cluster-cxiic4o4ihsm.us-east-1.rds.amazonaws.com")
RDS_USER = os.getenv("RDS_USER", "admin")
RDS_PASSWORD = os.getenv("RDS_PASSWORD", "Prathmesh")
RDS_DATABASE = os.getenv("RDS_DATABASE", "database-2")

# Step 1: Read from S3
def read_from_s3():
    try:
        logger.info("Connecting to S3...")
        s3 = boto3.client("s3")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_FILE_NAME)
        content = response["Body"].read().decode("utf-8")
        data = list(csv.reader(content.splitlines()))
        logger.info(f"Data read from S3 successfully: {len(data)} rows.")
        return data
    except NoCredentialsError:
        logger.error("S3 credentials not found.")
        return []
    except PartialCredentialsError:
        logger.error("Incomplete S3 credentials provided.")
        return []
    except Exception as e:
        logger.error(f"Error reading from S3: {e}")
        return []

# Step 2: Write to RDS
def write_to_rds(data):
    connection = None
    try:
        logger.info("Connecting to RDS...")
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DATABASE,
            connect_timeout=10  # Adjust timeout in seconds
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
        logger.info("Table checked/created successfully.")

        # Skip the header row and insert data
        for row in data[1:]:  # Skip header
            try:
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
            except Exception as e:
                logger.warning(f"Skipping row {row}: {e}")

        connection.commit()
        logger.info("Data written to RDS successfully.")
    except pymysql.MySQLError as e:
        logger.error(f"RDS operation failed: {e}")
    finally:
        if connection:
            connection.close()

# Main script
if __name__ == "__main__":
    # Step 1: Read data from S3
    s3_data = read_from_s3()

    if s3_data:
        # Step 2: Write data to RDS
        write_to_rds(s3_data)
    else:
        logger.info("No data to write.")
