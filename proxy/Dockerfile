FROM node as builder
ADD frontend /frontend
WORKDIR /frontend
RUN yarn && yarn generate
RUN cp -r dist /dist


FROM nginx
COPY --from=builder /dist /frontend
RUN chown -R nginx:nginx /frontend
ADD proxy/nginx_config.conf /etc/nginx/conf.d/default.conf

