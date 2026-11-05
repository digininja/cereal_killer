FROM node:18-alpine

WORKDIR /usr/src/app

# Copy dependency manifests and install
COPY package*.json ./
RUN npm install --omit=dev

# Copy application source code
COPY server.js ./

# Set up logging directory and permissions for the node user
RUN mkdir -p logs && chown -R node:node logs

USER node

EXPOSE 8000

CMD ["node", "server.js"]
