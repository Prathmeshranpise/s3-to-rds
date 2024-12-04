# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (Optional)
ENV S3_BUCKET_NAME="s386to98rds"
ENV S3_FILE_NAME="sample_data.csv"
ENV RDS_HOST="database-2.cluster-cxiic4o4ihsm.us-east-1.rds.amazonaws.com"
ENV RDS_USER="admin"
ENV RDS_PASSWORD="Prathmesh"
ENV RDS_DATABASE="database-2"

# Run main.py when the container launches
CMD ["python", "main.py"]
