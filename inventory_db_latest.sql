--
-- PostgreSQL database dump
--

\restrict sMGdhBYuY9VaVBJJb5zW3oqSqkwTkFDa6SE7y2pUMeQ1lERn3Xx2K4t73rWsthc

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

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
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    name character varying(50) NOT NULL,
    description character varying(255),
    created_at timestamp without time zone NOT NULL,
    id uuid CONSTRAINT categories_uuid_id_not_null NOT NULL
);


ALTER TABLE public.categories OWNER TO postgres;

--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    name character varying(100) NOT NULL,
    sku character varying(30) NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    quantity_in_stock integer NOT NULL,
    reorder_level integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id uuid CONSTRAINT products_uuid_id_not_null NOT NULL,
    category_id uuid CONSTRAINT products_uuid_category_id_not_null NOT NULL,
    supplier_id uuid CONSTRAINT products_uuid_supplier_id_not_null NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: revoked_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.revoked_tokens (
    id character varying(36) NOT NULL,
    jti character varying(36) NOT NULL,
    expires_at timestamp with time zone NOT NULL
);


ALTER TABLE public.revoked_tokens OWNER TO postgres;

--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suppliers (
    name character varying(100) NOT NULL,
    contact_email character varying(100) NOT NULL,
    phone character varying(15),
    address character varying(255),
    created_at timestamp without time zone NOT NULL,
    id uuid CONSTRAINT suppliers_uuid_id_not_null NOT NULL
);


ALTER TABLE public.suppliers OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    id uuid CONSTRAINT users_uuid_id_not_null NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
54b58217aa63
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categories (name, description, created_at, id) FROM stdin;
electronic	appliances	2026-08-25 10:49:34.322885	03d644b2-c214-48f3-9863-bb77aa3ab55b
Footwear		2026-08-26 17:19:19.253331	533a15dd-5c2d-4037-81f4-de00b87e68a2
Clothes	Things to wear on your body	2026-08-27 10:07:08.978267	ff848db9-35d3-4085-a45f-95aa4aee11bb
Cosmetics	 such as lipstck,foundation, concealor ,and skincare items.	2026-08-27 10:11:05.528518	6227c031-67ac-497d-9c8a-8caf5f6f6e5a
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (name, sku, unit_price, quantity_in_stock, reorder_level, is_active, created_at, updated_at, id, category_id, supplier_id) FROM stdin;
fridge	sam928	199222.00	3	2	t	2026-08-27 11:19:09.31997	2026-08-27 11:19:09.319973	733784bb-7a4b-45fa-a9c8-f23677d3a141	03d644b2-c214-48f3-9863-bb77aa3ab55b	8ff19537-9752-4646-8a4f-bc947fed6ce0
SHIRT	HM928	1321.00	10	0	t	2026-08-27 11:23:27.918025	2026-08-27 11:23:27.918028	942c6859-3af0-451b-a7d7-f21111d25b34	ff848db9-35d3-4085-a45f-95aa4aee11bb	c66934cb-26bd-4762-9561-0e39fb912518
Perfume	perf28	90000.00	0	0	t	2026-08-27 11:26:53.694581	2026-08-27 11:26:53.694585	2ff6766a-79cd-4561-87f7-963ff83db300	6227c031-67ac-497d-9c8a-8caf5f6f6e5a	59d630ec-3ef8-4ab3-a347-61a9207ce32a
Chic bowler bag	hiz -09	9000999.00	90000	1000	t	2026-08-27 11:30:18.33483	2026-08-27 11:30:18.334834	d8281ad9-3f59-4476-885c-81602bb7d46d	6227c031-67ac-497d-9c8a-8caf5f6f6e5a	d1b5bd18-55f3-4434-994c-e58f1112087a
Voltas	Voltas-12	10000.00	88	10	t	2026-08-25 10:56:19.715955	2026-09-03 15:58:59.537589	795403a1-d553-4e05-bf3b-b0c2b426d723	03d644b2-c214-48f3-9863-bb77aa3ab55b	8ff19537-9752-4646-8a4f-bc947fed6ce0
Nike AF1	AF -1uy7	10099.00	32	100000	f	2026-08-27 10:16:39.613873	2026-09-10 15:46:08.275383	202249e5-827c-471d-af48-b6c6c78da763	533a15dd-5c2d-4037-81f4-de00b87e68a2	dae3c283-d7bc-4871-9d4d-dab61892619a
Lip tint	tint28	13378.00	19	237	f	2026-08-27 11:25:02.325454	2026-09-10 15:47:16.901686	2ecc8361-85df-4d55-b4e2-e71a69c14fb9	6227c031-67ac-497d-9c8a-8caf5f6f6e5a	59d630ec-3ef8-4ab3-a347-61a9207ce32a
Skirt	sgh -0	9009.00	200	10	f	2026-08-27 11:35:54.218813	2026-09-10 15:49:03.056586	e1b116a4-e272-4e22-9e8c-7b098d72b062	ff848db9-35d3-4085-a45f-95aa4aee11bb	5c49dc7f-dea3-4382-9b4f-06a0f2c825c2
\.


--
-- Data for Name: revoked_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.revoked_tokens (id, jti, expires_at) FROM stdin;
43f1cf64-35a0-45a5-a954-e8f2b6a1ea10	7c36f781-514b-4dcd-bf90-168a579c1d81	2026-09-10 14:26:14+05:30
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suppliers (name, contact_email, phone, address, created_at, id) FROM stdin;
ABC_pvt_ltd	abc@example.com	3746282382	london	2026-08-25 10:55:22.170831	8ff19537-9752-4646-8a4f-bc947fed6ce0
Nike	user123@example.com	7364878233	America	2026-08-27 10:12:55.247957	dae3c283-d7bc-4871-9d4d-dab61892619a
samsung	sanr@example.com	8268899944	kolkata	2026-08-27 11:15:50.450422	25121ee8-0cf4-4e0b-acb0-a2b32fbc9f5b
H & M	HM@example.com	4762787122	UK	2026-08-27 11:21:41.007726	c66934cb-26bd-4762-9561-0e39fb912518
DIOR	DIOR@example.com	4762783322	FRANCE	2026-08-27 11:24:06.946668	59d630ec-3ef8-4ab3-a347-61a9207ce32a
Chanel	ch@example.com	4762783002	paris	2026-08-27 11:29:03.398177	d1b5bd18-55f3-4434-994c-e58f1112087a
Volchok	vikchk@example.com	476288882	Russia	2026-08-27 11:33:57.708053	5c49dc7f-dea3-4382-9b4f-06a0f2c825c2
jakson	jakson@gmail.com	5973053809	nsez	2026-09-08 13:30:39.605071	bf18376c-50bf-4a24-b24c-17ebad34f565
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (username, email, password_hash, role, id) FROM stdin;
ashish	ashish@example.com	$2b$12$LE9rm0aLB/x1a/w1xgn9e.P.VhvIzp710iix1Et2vcM1B67W7u46K	STAFF	ce55b388-2d9f-4ff8-8bec-87de33a9157a
Manya	manya@example.com	$2b$12$08FW0Oh.X6wvxVS0Gex5EODPMmLHm1NbLo/B5GU03OtV0Ad5qCWni	ADMIN	bccbae08-d440-442d-a3ed-8ca46c74b6be
Mana	mnya@example.com	$2b$12$5SGQcmxBU6BpTMoPIPfXle0nCLrVWVH03hcVAAaSaCEhv8yCXpSMS	AD	6679b03b-59ec-481b-bf0f-56d7d14d41ca
priyal	user@admin.com	$2b$12$jwfIP3UD4asG0JLqGefpPuCa1.sqKpyvxKLa1gQ4V6sxpFveaZNDK	ADMIN	63bbbd46-ff49-41bf-8ec3-32a08d62cc65
yug	yuvi@admin.com	$2b$12$tgwU.0s9lgwWXJ9HBwA9yOeqixDSIYT.3Cw29mI0h4YuRKmiazn7G	ADMIN	3a70ddab-d17b-479c-aa00-d87e159b9a42
ishu	ishu@staff.com	$2b$12$WOCO9WuHJERLmXt..lj1QeO6IRARAgjywMXw84YJc94WhytYziCqK	STAFF	9d10c710-9bf7-41f9-93e4-d8aadd089dd7
shivi	shivi@admin.com	$2b$12$HkNIfF/kznRJphQLM7Ou.OjmVM0WDpvbZYGHlyAxOoRTOSeyINC6u	ADMIN	bd2005ba-6eee-4f82-a0cb-736ad2f1ee70
dev	dev@admin.com	$2b$12$uI2uxcK6e8LIpaMCNnYJ7unmxDZ26JoUzclN9VWgkhC6qm7rUD7fu	ADMIN	a0498af7-257c-45f9-88cb-87b58c921bef
divyansh	devy@admin.com	$2b$12$IDvd59B3XWaz/0Bn/.L.cOim8YGcAf8n4Lf00bWDJUxi2YHqWQSce	ADMIN	0b8d71ed-4e5c-4b10-a5f9-7b2a416bd9d3
yumiko	yumiko@staff.com	$2b$12$MDLmbaFHFeyCTdNod5dvau.UbCHYWPD020I735UAyCjTbXTtn.Cg6	STAFF	caaf7bb4-b9fb-4019-9336-0801a1bd1e08
\.


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: products products_sku_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);


--
-- Name: revoked_tokens revoked_tokens_jti_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revoked_tokens
    ADD CONSTRAINT revoked_tokens_jti_key UNIQUE (jti);


--
-- Name: revoked_tokens revoked_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.revoked_tokens
    ADD CONSTRAINT revoked_tokens_pkey PRIMARY KEY (id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_suppliers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_suppliers_id ON public.suppliers USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: products products_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(id);


--
-- PostgreSQL database dump complete
--

\unrestrict sMGdhBYuY9VaVBJJb5zW3oqSqkwTkFDa6SE7y2pUMeQ1lERn3Xx2K4t73rWsthc

