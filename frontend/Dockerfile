# Use the official Node.js image
FROM node:24-slim

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the default Vite port
EXPOSE 5173

# Run the app in development mode with --host so it's accessible outside the container
CMD ["npm", "run", "dev", "--", "--host"]
