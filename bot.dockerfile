FROM node
#FROM node:10-slim
#RUN mkdir /opt/node_app && chown node:node /opt/node_app
RUN mkdir -p /opt/node_app
WORKDIR /opt/node_app
#USER node
COPY bot/ .
RUN npm install
#ENV PATH /opt/node_app/node_modules/.bin:$PATH

ENTRYPOINT ["node", "netbot.js"]