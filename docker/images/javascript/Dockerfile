FROM node:21-alpine3.17

WORKDIR /usr/src/app

RUN apk add bash
RUN npm update npm -g
RUN npm install nodemon -g
RUN npm install knex -g
RUN npm install -g @nestjs/cli
RUN npm install prisma@5.8.1

CMD (sed -i 's/\r$//' ./run.sh) ; (chmod +x ./run.sh) ; ./run.sh