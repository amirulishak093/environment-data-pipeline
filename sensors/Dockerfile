# Specify the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Create a Python virtual environment
RUN python -m venv env

# Activate the virtual environment
RUN . env/bin/activate

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code to the working directory
COPY . .

# Expose the port that your Flask app listens on
EXPOSE 2800

# Set the environment variables
ENV FLASK_APP=app.py

# Activate the virtual environment and run the Flask app
CMD ["python", "app.py"]

