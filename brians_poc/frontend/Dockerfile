# Development build for React frontend (simpler approach)
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Install serve for production serving
RUN npm install -g serve

# Expose port 80
EXPOSE 80

# Serve the built application
CMD ["serve", "-s", "dist", "-l", "80"]