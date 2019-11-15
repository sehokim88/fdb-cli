create table ss_pwds (
    id serial primary key,
    pwd varchar not null
);


create table subscribers (
    id serial primary key,
    first_name varchar not null,
    last_name varchar not null,
    email varchar not null,
    dob date not null,
    "role" varchar,
    pwd_id int2 references ss_pwds(id)
);


create table sj_pwds (
    id serial primary key,
    pwd varchar not null
);


create table subjects (
    id serial primary key,
    first_name varchar not null,
    last_name varchar not null,
    email varchar not null,
    dob date not null,
    ss_id int2 references subscribers(id),
    pwd_id int2 references sj_pwds(id)
);


