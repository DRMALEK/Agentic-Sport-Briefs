FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps and force flag to resolve conflicts
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
