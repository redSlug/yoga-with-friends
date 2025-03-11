FROM alpine:3.21.3

RUN apk add --no-cache \
    nodejs \
    npm \
    python3 \
    py3-pip \
    curl


WORKDIR /yoga-with-friends/backend

COPY backend/requirements.txt .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

WORKDIR /yoga-with-friends/frontend

COPY frontend/package.json .

RUN npm install -g --no-cache-dir --break-system-packages

RUN npm install @rollup/rollup-linux-x64-musl --save-dev

RUN npm rebuild rollup

WORKDIR /yoga-with-friends

ADD . .

WORKDIR /yoga-with-friends/frontend

ENV PATH=$PATH:/yoga-with-friends/frontend/node_modules/.bin

CMD ["npm", "run", "deploy"]
