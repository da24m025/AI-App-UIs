# 1. Use official Node.js 18 slim image
FROM node:18-alpine

# 2. Create app directory
WORKDIR /app

# 3. Copy package manifests first (for caching)
COPY package.json package-lock.json ./

# 4. Install dependencies
RUN npm ci

# 5. Copy the rest of your React app
COPY public ./public
COPY src    ./src

# 6. Expose the port and set default command
EXPOSE 3000
CMD ["npm", "start"]
