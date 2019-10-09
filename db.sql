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


-- insert into ss_passwords
-- values (default, 'bs042825');

-- insert into subscribers
-- values (default, 'Seho', 'Kim', 'sehokim88@gmail.com', '1991-04-25', 'researcher', 1);

-- insert into sj_passwords
-- values (default, 'bs042825');

-- insert into subjects
-- values (default, 'Seho', 'Kim', 'sehokim88@gmail.com', '1991-04-25', '7BVHQT', 1, 1);

-- insert into sj_passwords
-- values (default, 'bs042825');

-- insert into subjects
-- values (default, 'Brittney', 'Kim', 'briwynn28@gmail.com', '1990-04-28', '74NFBJ', 1, 2);