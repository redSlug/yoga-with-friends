FROM alpine:3.21.3

RUN apk add --no-cache \
    nodejs \
    npm \
    python3 \
    py3-pip \
    curl


WORKDIR /yoga-not-fees

COPY backend/requirements.txt .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY frontend/package-lock.json .

RUN npm install -g --no-cache-dir --break-system-packages

ADD . .

CMD npm run deploy
