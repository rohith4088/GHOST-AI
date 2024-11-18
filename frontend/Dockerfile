# Use an official Node runtime as the parent image
FROM node:16

# Set the working directory in the container to /app
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install any needed packages specified in package.json
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build
EXPOSE 80
# Serve the app
CMD ["npm", "start"]