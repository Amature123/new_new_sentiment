
FROM alpine:3.20
WORKDIR /app  
COPY package.json /app  
RUN npm install  
COPY . /app  
EXPOSE git   
CMD node index.js
