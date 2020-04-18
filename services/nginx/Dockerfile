FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/mysite.template
COPY index.html /etc/nginx/html/
