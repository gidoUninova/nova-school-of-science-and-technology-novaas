FROM nikolaik/python-nodejs:python3.9-nodejs14-slim
LABEL org.opencontainers.image.authors="gido@uninova.pt"
RUN apt-get update && apt install unzip && apt-get install -y git && apt install -y sqlite3 && apt-get install -y netcat \
&& npm install -g --unsafe-perm node-red
WORKDIR /app
RUN mkdir -p .node-red
ADD files .node-red/
# Adding Flexdash dependecies and core widgets ************************
RUN npm i @flexdash/node-red-fd-corewidgets --prefix /app/.node-red
# *********************************************************************
RUN npm install --prefix /app/.node-red
RUN npm i passport
RUN npm i passport-keycloak-oauth2-oidc
ADD dist .node-red/node_modules/node-red-dashboard/dist/
RUN unzip /app/.node-red/model.aasx -d /app/.node-red/
RUN /usr/bin/sqlite3 /db/inNOVAASdb.db
EXPOSE 1880
ENTRYPOINT ["node-red", "-u", "/app/.node-red", "-s", "/app/.node-red/settings.js"]
