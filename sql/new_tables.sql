--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.2
-- Dumped by pg_dump version 9.5.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

CREATE TYPE public.timerange AS RANGE(
	subtype = TIME
);

--
-- Name: congestion; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA congestion;


SET search_path = congestion, pg_catalog;

SET default_with_oids = false;

--
-- Name: aggregation_levels; Type: TABLE; Schema: congestion; Owner: -
--

CREATE TABLE aggregation_levels (
    agg_id smallint NOT NULL,
    agg_level character varying(9) NOT NULL
);

--
-- Name: aggregation_levels_agg_id_seq; Type: SEQUENCE; Schema: congestion; Owner: -
--

CREATE SEQUENCE aggregation_levels_agg_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: aggregation_levels_agg_id_seq; Type: SEQUENCE OWNED BY; Schema: congestion; Owner: -
--

ALTER SEQUENCE aggregation_levels_agg_id_seq OWNED BY aggregation_levels.agg_id;


--
-- Name: metrics; Type: TABLE; Schema: congestion; Owner: -
--

CREATE TABLE metrics (
    tmc character(9),
    timeperiod timerange,
    agg_id smallint,
    agg_period date,
    tti real,
    bti real
);


--
-- Name: map_metrics; Type: TABLE; Schema: congestion; Owner: -
--


CREATE TABLE map_metrics
(
  "Rank" smallint,
  "Street" TEXT,
  "Dir" TEXT,
  "From - To" TEXT,
  "Metric" TEXT,
  geom Geometry
);
COMMENT ON TABLE map_metrics IS 'Abstract table to return layers for mapping in a plgpsql function';


--
-- Name: agg_id; Type: DEFAULT; Schema: congestion; Owner: -
--

ALTER TABLE ONLY aggregation_levels ALTER COLUMN agg_id SET DEFAULT nextval('aggregation_levels_agg_id_seq'::regclass);


--
-- Name: aggregation_levels_pkey; Type: CONSTRAINT; Schema: congestion; Owner: -
--

ALTER TABLE ONLY aggregation_levels
    ADD CONSTRAINT aggregation_levels_pkey PRIMARY KEY (agg_id);


--
-- PostgreSQL database dump complete
--

