FROM nikolaik/python-nodejs:python3.11-nodejs18
LABEL org.opencontainers.image.authors="gido@uninova.pt"
ARG AAS_VERSION=V2
RUN apt-get update && apt-get install -y apt-utils && apt install unzip && apt-get install -y git && apt install -y sqlite3 && apt-get install -y netcat-traditional \
&& npm install -g --unsafe-perm node-red
WORKDIR /app
RUN mkdir -p .node-red
ADD files .node-red/
# Adding Flexdash dependecies and core widgets ************************
#RUN npm i @flexdash/node-red-fd-corewidgets --prefix /app/.node-red
# *********************************************************************
RUN npm install --prefix /app/.node-red
RUN npm i passport
RUN npm i passport-keycloak-oauth2-oidc
ADD dist .node-red/node_modules/node-red-dashboard/dist/
RUN unzip /app/.node-red/model.aasx -d /app/.node-red/
RUN /usr/bin/sqlite3 /db/inNOVAASdb.db
RUN apt install jq -y
#RUN jq -s 'flatten | group_by(.id) | map(reduce .[] as $x ({}; . * $x))' \
#    /app/.node-red/flows_gido-VirtualBox.json /app/.node-red/flow_asset_user_interface.json > /app/.node-red/flows_aux.json \
#    && mv /app/.node-red/flows_aux.json /app/.node-red/flows_gido-VirtualBox.json
# RUN jq -s '.[0] * .[1]' /app/.node-red/a.json /app/.node-red/b.json >> /app/.node-red/c.json
# RUN cat /app/.node-red/c.json

RUN if [ "${AAS_VERSION}" = "V2" ]; then \
        jq 'map(if .label == "AAS - Environment V3" or .label == "AAS - UserInterface V3" then .disabled = true elif .label == "AAS - Environment V2" or .label == "AAS - UserInterface V2" then .disabled = false else . end)' /app/.node-red/flows_gido-VirtualBox.json > /app/.node-red/flows_gido-VirtualBox_aux.json \
        && mv /app/.node-red/flows_gido-VirtualBox_aux.json /app/.node-red/flows_gido-VirtualBox.json; \
    else \
        jq 'map(if .label == "AAS - Environment V3" or .label == "AAS - UserInterface V3" then .disabled = false elif .label == "AAS - Environment V2" or .label == "AAS - UserInterface V2" then .disabled = true else . end)' /app/.node-red/flows_gido-VirtualBox.json > /app/.node-red/flows_gido-VirtualBox_aux.json \
        && mv /app/.node-red/flows_gido-VirtualBox_aux.json /app/.node-red/flows_gido-VirtualBox.json; \
    fi
EXPOSE 1880
ENTRYPOINT ["node-red", "-u", "/app/.node-red", "-s", "/app/.node-red/settings.js"]
