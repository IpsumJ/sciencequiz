--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.3
-- Dumped by pg_dump version 9.6.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
    id integer NOT NULL,
    description character varying(300) NOT NULL
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
    category integer NOT NULL,
    correct integer DEFAULT '-1'::integer NOT NULL
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
-- Name: questions_correct_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE questions_correct_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE questions_correct_seq OWNER TO scq;

--
-- Name: questions_correct_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE questions_correct_seq OWNED BY questions.correct;


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
-- Name: quiz_questions; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE quiz_questions (
    index integer NOT NULL,
    id integer NOT NULL,
    question integer NOT NULL,
    quiz integer NOT NULL
);


ALTER TABLE quiz_questions OWNER TO scq;

--
-- Name: quiz_questions_quiz_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE quiz_questions_quiz_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE quiz_questions_quiz_seq OWNER TO scq;

--
-- Name: quiz_questions_quiz_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE quiz_questions_quiz_seq OWNED BY quiz_questions.quiz;


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

ALTER SEQUENCE quiz_questsions_id_seq OWNED BY quiz_questions.id;


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

ALTER SEQUENCE quiz_questsions_question_seq OWNED BY quiz_questions.question;


--
-- Name: quizes; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE quizes (
    year integer NOT NULL,
    name character varying(200),
    id integer NOT NULL,
    public boolean DEFAULT false NOT NULL
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
-- Name: sessions; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE sessions (
    id integer NOT NULL,
    quiz integer NOT NULL,
    team integer NOT NULL
);


ALTER TABLE sessions OWNER TO scq;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sessions_id_seq OWNER TO scq;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE sessions_id_seq OWNED BY sessions.id;


--
-- Name: sessions_quiz_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE sessions_quiz_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sessions_quiz_seq OWNER TO scq;

--
-- Name: sessions_quiz_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE sessions_quiz_seq OWNED BY sessions.quiz;


--
-- Name: sessions_team_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE sessions_team_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sessions_team_seq OWNER TO scq;

--
-- Name: sessions_team_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE sessions_team_seq OWNED BY sessions.team;


--
-- Name: team_answers; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE team_answers (
    id integer NOT NULL,
    team_session integer NOT NULL,
    answer integer NOT NULL
);


ALTER TABLE team_answers OWNER TO scq;

--
-- Name: team_answers_answer_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_answers_answer_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_answers_answer_seq OWNER TO scq;

--
-- Name: team_answers_answer_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_answers_answer_seq OWNED BY team_answers.answer;


--
-- Name: team_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_answers_id_seq OWNER TO scq;

--
-- Name: team_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_answers_id_seq OWNED BY team_answers.id;


--
-- Name: team_answers_team_session_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_answers_team_session_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_answers_team_session_seq OWNER TO scq;

--
-- Name: team_answers_team_session_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_answers_team_session_seq OWNED BY team_answers.team_session;


--
-- Name: team_memberships; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE team_memberships (
    team integer NOT NULL,
    "user" integer NOT NULL
);


ALTER TABLE team_memberships OWNER TO scq;

--
-- Name: team_memberships_team_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_memberships_team_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_memberships_team_seq OWNER TO scq;

--
-- Name: team_memberships_team_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_memberships_team_seq OWNED BY team_memberships.team;


--
-- Name: team_memberships_user_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_memberships_user_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_memberships_user_seq OWNER TO scq;

--
-- Name: team_memberships_user_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_memberships_user_seq OWNED BY team_memberships."user";


--
-- Name: team_sessions; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE team_sessions (
    id integer NOT NULL,
    team integer NOT NULL,
    session integer NOT NULL
);


ALTER TABLE team_sessions OWNER TO scq;

--
-- Name: team_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_sessions_id_seq OWNER TO scq;

--
-- Name: team_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_sessions_id_seq OWNED BY team_sessions.id;


--
-- Name: team_sessions_session_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_sessions_session_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_sessions_session_seq OWNER TO scq;

--
-- Name: team_sessions_session_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_sessions_session_seq OWNED BY team_sessions.session;


--
-- Name: team_sessions_team_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE team_sessions_team_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_sessions_team_seq OWNER TO scq;

--
-- Name: team_sessions_team_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE team_sessions_team_seq OWNED BY team_sessions.team;


--
-- Name: teams; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE teams (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    year integer NOT NULL
);


ALTER TABLE teams OWNER TO scq;

--
-- Name: teams_id_seq; Type: SEQUENCE; Schema: public; Owner: scq
--

CREATE SEQUENCE teams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE teams_id_seq OWNER TO scq;

--
-- Name: teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: scq
--

ALTER SEQUENCE teams_id_seq OWNED BY teams.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: scq
--

CREATE TABLE users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password character varying(512) NOT NULL,
    admin boolean NOT NULL,
    display_name character varying(100) NOT NULL,
    email character varying(100) NOT NULL
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
-- Name: answers answers; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers ALTER COLUMN answers SET DEFAULT nextval('answers_answers_seq'::regclass);


--
-- Name: answers id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers ALTER COLUMN id SET DEFAULT nextval('answers_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY categories ALTER COLUMN id SET DEFAULT nextval('categories_id_seq'::regclass);


--
-- Name: device_api_tokens id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY device_api_tokens ALTER COLUMN id SET DEFAULT nextval('device_api_tokens_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions ALTER COLUMN id SET DEFAULT nextval('questions_id_seq'::regclass);


--
-- Name: questions category; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions ALTER COLUMN category SET DEFAULT nextval('questions_category_seq'::regclass);


--
-- Name: quiz_questions id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions ALTER COLUMN id SET DEFAULT nextval('quiz_questsions_id_seq'::regclass);


--
-- Name: quiz_questions question; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions ALTER COLUMN question SET DEFAULT nextval('quiz_questsions_question_seq'::regclass);


--
-- Name: quiz_questions quiz; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions ALTER COLUMN quiz SET DEFAULT nextval('quiz_questions_quiz_seq'::regclass);


--
-- Name: quizes id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quizes ALTER COLUMN id SET DEFAULT nextval('quizes_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions ALTER COLUMN id SET DEFAULT nextval('sessions_id_seq'::regclass);


--
-- Name: sessions quiz; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions ALTER COLUMN quiz SET DEFAULT nextval('sessions_quiz_seq'::regclass);


--
-- Name: sessions team; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions ALTER COLUMN team SET DEFAULT nextval('sessions_team_seq'::regclass);


--
-- Name: team_answers id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_answers ALTER COLUMN id SET DEFAULT nextval('team_answers_id_seq'::regclass);


--
-- Name: team_answers team_session; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_answers ALTER COLUMN team_session SET DEFAULT nextval('team_answers_team_session_seq'::regclass);


--
-- Name: team_answers answer; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_answers ALTER COLUMN answer SET DEFAULT nextval('team_answers_answer_seq'::regclass);


--
-- Name: team_memberships team; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_memberships ALTER COLUMN team SET DEFAULT nextval('team_memberships_team_seq'::regclass);


--
-- Name: team_memberships user; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_memberships ALTER COLUMN "user" SET DEFAULT nextval('team_memberships_user_seq'::regclass);


--
-- Name: team_sessions id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions ALTER COLUMN id SET DEFAULT nextval('team_sessions_id_seq'::regclass);


--
-- Name: team_sessions team; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions ALTER COLUMN team SET DEFAULT nextval('team_sessions_team_seq'::regclass);


--
-- Name: team_sessions session; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions ALTER COLUMN session SET DEFAULT nextval('team_sessions_session_seq'::regclass);


--
-- Name: teams id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY teams ALTER COLUMN id SET DEFAULT nextval('teams_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: scq
--

ALTER TABLE ONLY users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Name: answers answers_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers
    ADD CONSTRAINT answers_id_pk PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: device_api_tokens device_api_tokens_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY device_api_tokens
    ADD CONSTRAINT device_api_tokens_id_pk PRIMARY KEY (id);


--
-- Name: questions questions_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_id_pk PRIMARY KEY (id);


--
-- Name: quiz_questions quiz_questions_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions
    ADD CONSTRAINT quiz_questions_id_pk PRIMARY KEY (id);


--
-- Name: quizes quizes_id_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quizes
    ADD CONSTRAINT quizes_id_pk PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: team_memberships team_memberships_user_team_pk; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_memberships
    ADD CONSTRAINT team_memberships_user_team_pk PRIMARY KEY ("user", team);


--
-- Name: team_sessions team_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions
    ADD CONSTRAINT team_sessions_pkey PRIMARY KEY (id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: scq
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
-- Name: quiz_questions_index_quiz_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX quiz_questions_index_quiz_uindex ON quiz_questions USING btree (index, quiz);


--
-- Name: quiz_questions_question_quiz_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX quiz_questions_question_quiz_uindex ON quiz_questions USING btree (question, quiz);


--
-- Name: quizes_year_name_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX quizes_year_name_uindex ON quizes USING btree (year, name);


--
-- Name: team_sessions_team_session_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX team_sessions_team_session_uindex ON team_sessions USING btree (team, session);


--
-- Name: teams_name_year_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX teams_name_year_uindex ON teams USING btree (name, year);


--
-- Name: users_username_uindex; Type: INDEX; Schema: public; Owner: scq
--

CREATE UNIQUE INDEX users_username_uindex ON users USING btree (username);


--
-- Name: answers answers_questions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY answers
    ADD CONSTRAINT answers_questions_id_fk FOREIGN KEY (answers) REFERENCES questions(id) ON DELETE CASCADE;


--
-- Name: questions questions_categories_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY questions
    ADD CONSTRAINT questions_categories_id_fk FOREIGN KEY (category) REFERENCES categories(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: quiz_questions quiz_questions_quizes_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions
    ADD CONSTRAINT quiz_questions_quizes_id_fk FOREIGN KEY (quiz) REFERENCES quizes(id);


--
-- Name: quiz_questions quiz_questsions_questions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY quiz_questions
    ADD CONSTRAINT quiz_questsions_questions_id_fk FOREIGN KEY (question) REFERENCES questions(id);


--
-- Name: sessions sessions_quizes_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_quizes_id_fk FOREIGN KEY (quiz) REFERENCES quizes(id);


--
-- Name: sessions sessions_teams_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_teams_id_fk FOREIGN KEY (team) REFERENCES teams(id);


--
-- Name: team_answers team_answers_answers_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_answers
    ADD CONSTRAINT team_answers_answers_id_fk FOREIGN KEY (answer) REFERENCES answers(id);


--
-- Name: team_answers team_answers_team_sessions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_answers
    ADD CONSTRAINT team_answers_team_sessions_id_fk FOREIGN KEY (team_session) REFERENCES team_sessions(id);


--
-- Name: team_memberships team_memberships_teams_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_memberships
    ADD CONSTRAINT team_memberships_teams_id_fk FOREIGN KEY (team) REFERENCES teams(id);


--
-- Name: team_memberships team_memberships_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_memberships
    ADD CONSTRAINT team_memberships_users_id_fk FOREIGN KEY ("user") REFERENCES users(id);


--
-- Name: team_sessions team_sessions_sessions_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions
    ADD CONSTRAINT team_sessions_sessions_id_fk FOREIGN KEY (session) REFERENCES sessions(id);


--
-- Name: team_sessions team_sessions_teams_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: scq
--

ALTER TABLE ONLY team_sessions
    ADD CONSTRAINT team_sessions_teams_id_fk FOREIGN KEY (team) REFERENCES teams(id);


--
-- PostgreSQL database dump complete
--

