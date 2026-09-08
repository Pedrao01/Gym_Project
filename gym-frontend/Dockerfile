# stage 1 - build
FROM node:20-alpine AS build
WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# stage 2 - delivery
FROM alpine:3.20
WORKDIR /app
COPY --from=build /build/dist ./dist_build

CMD ["sh", "-c", "rm -rf /app/dist/* && cp -r /app/dist_build/* /app/dist/ && echo 'Frontend build copiado para o volume.'"]
