# Шаг 1: Сборка React приложения
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Шаг 2: Раздача статики через Nginx
FROM nginx:stable-alpine
# Копируем билд в папку, откуда Nginx раздает файлы
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]