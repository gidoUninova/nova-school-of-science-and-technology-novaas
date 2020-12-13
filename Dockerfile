FROM node:12.19-slim
RUN apt-get update && apt-get install python-pip -y \
snmpd \  
&& etc/init.d/snmpd restart \
&& npm install -g --unsafe-perm node-red
WORKDIR /app
RUN mkdir -p .node-red
ADD files .node-red/
RUN npm install --prefix /app/.node-red
EXPOSE 1880
ENTRYPOINT ["node-red", "-u", "/app/.node-red", "-s", "/app/.node-red/settings.js"]
