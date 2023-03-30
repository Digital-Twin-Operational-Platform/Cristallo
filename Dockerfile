# Base image
FROM python:3.8.0-slim

# Set working directory
WORKDIR /digitaltwin

# Copy the Flask app to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the app will run
EXPOSE 5000

# Start the Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "digitaltwin:create_app()"]