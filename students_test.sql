--
-- PostgreSQL database dump
--

\restrict 1r0SAIhSpR9bdAHpN35Bu9KZXu2jgXzWYIvYm1wiuUmJKJTEacWrtGvWgGU29la

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: students_student; Type: TABLE DATA; Schema: public; Owner: xoradex_app
--

COPY public.students_student (id, admission_no, first_name, middle_name, last_name, gender, date_of_birth, id_number, phone, email, address, admission_date, created_at, updated_at, programme_id, user_id, status) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

\unrestrict 1r0SAIhSpR9bdAHpN35Bu9KZXu2jgXzWYIvYm1wiuUmJKJTEacWrtGvWgGU29la

