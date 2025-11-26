CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS user (
    id SERIAL PRIMARY KEY,
    discord_id BIGINT,
    avatar_url TEXT
);

CREATE SCHEMA IF NOT EXISTS note;
CREATE TABLE IF NOT EXISTS note.content (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    updated_at TIMESTAMP,
    author_id BIGINT
);

CREATE TABLE IF NOT EXISTS note.embedding (
    note_id BIGINT REFERENCES note.metadata(id),
    model VARCHAR(128),
    embedding VECTOR(384), -- size of output of text-embedding-3-small model 
    PRIMARY KEY(note_id, model)
);

CREATE TABLE IF NOT EXISTS note.rules (
    note_id BIGINT REFERENCES note.metadata(id),
    editor_id BIGINT,
    PRIMARY KEY(note_id, editor_id)
);


CREATE SCHEMA IF NOT EXISTS role;
CREATE TABLE IF NOT EXISTS role.metadata (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role.permission (
    role_id BIGINT REFERENCES role.metadata(id),
    note_id BIGINT REFERENCES note.content(id),
    permission SMALLINT, -- like UNIX with rwx
    PRIMARY KEY (role_id, note_id)
);

CREATE TABLE IF NOT EXISTS role.member (
    role_id BIGINT REFERENCES role.metadata(id),
    member_id BIGINT REFERENCES user(id),
    PRIMARY KEY(role_id, member_id)
);