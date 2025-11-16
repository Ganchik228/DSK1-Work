create schema telegram_bot;

create table telegram_bot.roles (
    id uuid primary key,
    name varchar
);

create table telegram_bot.users (
    id uuid primary key,
    chat_id varchar,
    name varchar
);

create table telegram_bot.reviews (
    id uuid primary key,
    comment varchar,
    user_id uuid,
    role_id uuid,
    foreign key (user_id) references telegram_bot.users(id),
    foreign key (role_id) references telegram_bot.roles(id),
    date_time timestamp
);

INSERT INTO telegram_bot.roles VALUES (gen_random_uuid(), 'Сотрудник');
INSERT INTO telegram_bot.roles VALUES (gen_random_uuid(), 'Клиент');
INSERT INTO telegram_bot.roles VALUES (gen_random_uuid(), 'Партнер');