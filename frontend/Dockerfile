# Use Node 18 Alpine image as base
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy frontend code
COPY . .

# Expose Next.js port
EXPOSE 3000

# Run Next.js development server
CMD ["npm", "run", "dev"]
