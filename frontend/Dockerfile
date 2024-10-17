FROM oven/bun:alpine

WORKDIR /frontend

COPY package.json ./

COPY bun.lockb ./

RUN bun install

COPY . .

RUN bun run build

RUN rm -rf src public postcss.config.cjs tailwind.config.ts

ENTRYPOINT ["bun", "run", "preview"]
