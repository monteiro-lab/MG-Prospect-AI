# Use Nginx to serve the pre-built files
FROM nginx:alpine

# Remove a config default do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia a config customizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia o build pre-compilado do React
COPY dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
