--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.3
-- Dumped by pg_dump version 9.5.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: answers; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE answers (
    answer text NOT NULL,
    answers integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE answers OWNER TO scq;

--
-- Name: answers_answers_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE answers_answers_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE answers_answers_seq OWNER TO scq;

--
-- Name: answers_answers_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE answers_answers_seq OWNED BY answers.answers;


--
-- Name: answers_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE answers_id_seq OWNER TO scq;

--
-- Name: answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE answers_id_seq OWNED BY answers.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE categories OWNER TO scq;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE categories_id_seq OWNER TO scq;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE categories_id_seq OWNED BY categories.id;


--
-- Name: device_api_tokens; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE device_api_tokens (
    token character varying(200) NOT NULL,
    id integer NOT NULL
);


ALTER TABLE device_api_tokens OWNER TO scq;

--
-- Name: device_api_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE device_api_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE device_api_tokens_id_seq OWNER TO scq;

--
-- Name: device_api_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE device_api_tokens_id_seq OWNED BY device_api_tokens.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE questions (
    question text NOT NULL,
    image text,
    id integer NOT NULL,
    category integer NOT NULL
);


ALTER TABLE questions OWNER TO scq;

--
-- Name: questions_category_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE questions_category_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE questions_category_seq OWNER TO scq;

--
-- Name: questions_category_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE questions_category_seq OWNED BY questions.category;


--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE questions_id_seq OWNER TO scq;

--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE questions_id_seq OWNED BY questions.id;


--
-- Name: quiz_questsions; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE quiz_questsions (
    index integer NOT NULL,
    id integer NOT NULL,
    question integer NOT NULL
);


ALTER TABLE quiz_questsions OWNER TO scq;

--
-- Name: quiz_questsions_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE quiz_questsions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE quiz_questsions_id_seq OWNER TO scq;

--
-- Name: quiz_questsions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE quiz_questsions_id_seq OWNED BY quiz_questsions.id;


--
-- Name: quiz_questsions_question_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE quiz_questsions_question_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE quiz_questsions_question_seq OWNER TO scq;

--
-- Name: quiz_questsions_question_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE quiz_questsions_question_seq OWNED BY quiz_questsions.question;


--
-- Name: quizes; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE quizes (
    year integer NOT NULL,
    name character varying(200),
    id integer NOT NULL
);


ALTER TABLE quizes OWNER TO scq;

--
-- Name: quizes_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE quizes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE quizes_id_seq OWNER TO scq;

--
-- Name: quizes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE quizes_id_seq OWNED BY quizes.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password character varying(256) NOT NULL,
    can_arrange_quiz boolean NOT NULL
);


ALTER TABLE users OWNER TO scq;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE users_id_seq OWNER TO scq;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: answers; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers ALTER COLUMN answers SET DEFAULT nextval('answers_answers_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers ALTER COLUMN id SET DEFAULT nextval('answers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY categories ALTER COLUMN id SET DEFAULT nextval('categories_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY device_api_tokens ALTER COLUMN id SET DEFAULT nextval('device_api_tokens_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions ALTER COLUMN id SET DEFAULT nextval('questions_id_seq'::regclass);


--
-- Name: category; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions ALTER COLUMN category SET DEFAULT nextval('questions_category_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questsions ALTER COLUMN id SET DEFAULT nextval('quiz_questsions_id_seq'::regclass);


--
-- Name: question; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questsions ALTER COLUMN question SET DEFAULT nextval('quiz_questsions_question_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quizes ALTER COLUMN id SET DEFAULT nextval('quizes_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Data for Name: answers; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY answers (answer, answers, id) FROM stdin;
\.


--
-- Name: answers_answers_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('answers_answers_seq', 1, false);


--
-- Name: answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('answers_id_seq', 1, false);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY categories (id, name) FROM stdin;
\.


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('categories_id_seq', 1, false);


--
-- Data for Name: device_api_tokens; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY device_api_tokens (token, id) FROM stdin;
\.


--
-- Name: device_api_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('device_api_tokens_id_seq', 1, false);


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY questions (question, image, id, category) FROM stdin;
\.


--
-- Name: questions_category_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('questions_category_seq', 1, false);


--
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('questions_id_seq', 1, false);


--
-- Data for Name: quiz_questsions; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY quiz_questsions (index, id, question) FROM stdin;
\.


--
-- Name: quiz_questsions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('quiz_questsions_id_seq', 1, false);


--
-- Name: quiz_questsions_question_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('quiz_questsions_question_seq', 1, false);


--
-- Data for Name: quizes; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY quizes (year, name, id) FROM stdin;
\.


--
-- Name: quizes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('quizes_id_seq', 1, false);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: scq
--

COPY users (id, username, password, can_arrange_quiz) FROM stdin;
\.


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: scq
--

SELECT pg_catalog.setval('users_id_seq', 1, false);


--
-- Name: answers_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers
    ADD CONSTRAINT answers_id_pk PRIMARY KEY (id);


--
-- Name: categories_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: device_api_tokens_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY device_api_tokens
    ADD CONSTRAINT device_api_tokens_id_pk PRIMARY KEY (id);


--
-- Name: questions_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_id_pk PRIMARY KEY (id);


--
-- Name: quiz_questsions_index_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questsions
    ADD CONSTRAINT quiz_questsions_index_pk PRIMARY KEY (index);


--
-- Name: quizes_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quizes
    ADD CONSTRAINT quizes_id_pk PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: categories_name_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX categories_name_uindex ON categories USING btree (name);


--
-- Name: device_api_tokens_token_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX device_api_tokens_token_uindex ON device_api_tokens USING btree (token);


--
-- Name: users_username_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX users_username_uindex ON users USING btree (username);


--
-- Name: answers_questions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers
    ADD CONSTRAINT answers_questions_id_fk FOREIGN KEY (answers) REFERENCES questions(id);


--
-- Name: questions_categories_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_categories_id_fk FOREIGN KEY (category) REFERENCES categories(id);


--
-- Name: quiz_questsions_questions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questsions
    ADD CONSTRAINT quiz_questsions_questions_id_fk FOREIGN KEY (question) REFERENCES questions(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

