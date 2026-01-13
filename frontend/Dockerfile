FROM node:18

WORKDIR /app

COPY package.json package-lock.json ./

# Instalujemy wszystkie zależności + react-chartjs-2
RUN npm install react-chartjs-2 chart.js && npm install

COPY . .

RUN npm run build

CMD ["npm", "start"]
