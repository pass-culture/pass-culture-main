--
-- PostgreSQL database dump
--

-- Dumped from database version 10.1
-- Dumped by pg_dump version 10.1

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

-- COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: eventtype; Type: TYPE; Schema: public; 
--

CREATE TYPE eventtype AS ENUM (
    'Workshop',
    'MovieScreening',
    'Meeting',
    'Game',
    'SchoolHelp',
    'StreetPerformance',
    'Other',
    'BookReading',
    'CircusAndMagic',
    'DancePerformance',
    'Comedy',
    'Concert',
    'Combo',
    'Youth',
    'Musical',
    'Theater',
    'GuidedVisit',
    'FreeVisit'
);



--
-- Name: localprovidereventtype; Type: TYPE; Schema: public; 
--

CREATE TYPE localprovidereventtype AS ENUM (
    'SyncError',
    'SyncPartStart',
    'SyncPartEnd',
    'SyncStart',
    'SyncEnd'
);



--
-- Name: rightstype; Type: TYPE; Schema: public; 
--

CREATE TYPE rightstype AS ENUM (
    'admin',
    'editor'
);




--
-- Name: check_booking(); Type: FUNCTION; Schema: public; 
--

CREATE FUNCTION check_booking() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM offer WHERE id=NEW."offerId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM offer WHERE id=NEW."offerId")
              < (SELECT COUNT(*) FROM booking WHERE "offerId"=NEW."offerId")) THEN
          RAISE EXCEPTION 'Offer has too many bookings'
                USING HINT = 'Number of bookings cannot exceed "offer.available"';
      END IF;
      RETURN NEW;
    END;
    $$;



--
-- Name: check_offer(); Type: FUNCTION; Schema: public; 
--

CREATE FUNCTION check_offer() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF NOT NEW.available IS NULL AND
      ((SELECT COUNT(*) FROM booking WHERE "offerId"=NEW.id) > NEW.available) THEN
        RAISE EXCEPTION 'available_too_low'
              USING HINT = 'offer.available cannot be lower than number of bookings';
      END IF;

      IF NOT NEW."bookingLimitDatetime" IS NULL AND
      (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurence WHERE id=NEW."eventOccurenceId")) THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT  = 'offer.bookingLimitDatetime after event_occurence.beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$;



--
-- Name: jsonb_change_key_name(jsonb, text, text); Type: FUNCTION; Schema: public; 
--

CREATE FUNCTION jsonb_change_key_name(data jsonb, old_key text, new_key text) RETURNS jsonb
    LANGUAGE sql IMMUTABLE
    AS $$
    SELECT ('{'||string_agg(to_json(CASE WHEN key = old_key THEN new_key ELSE key END)||':'||value, ',')||'}')::jsonb
    FROM (
        SELECT *
        FROM jsonb_each(data)
    ) t;
$$;



--
-- Name: jsonb_subtract(jsonb, jsonb); Type: FUNCTION; Schema: public; 
--

CREATE FUNCTION jsonb_subtract(arg1 jsonb, arg2 jsonb) RETURNS jsonb
    LANGUAGE sql
    AS $$
SELECT
  COALESCE(json_object_agg(key, value), '{}')::jsonb
FROM
  jsonb_each(arg1)
WHERE
  (arg1 -> key) <> (arg2 -> key) OR (arg2 -> key) IS NULL
$$;



--
-- Name: -; Type: OPERATOR; Schema: public; 
--

CREATE OPERATOR - (
    PROCEDURE = jsonb_subtract,
    LEFTARG = jsonb,
    RIGHTARG = jsonb
);



SET default_tablespace = '';

SET default_with_oids = false;


--
-- Name: activity; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE activity (
    id bigint NOT NULL,
    schema_name text,
    table_name text,
    relid integer,
    issued_at timestamp without time zone,
    native_transaction_id bigint,
    verb text,
    old_data jsonb DEFAULT '{}'::jsonb,
    changed_data jsonb DEFAULT '{}'::jsonb,
    transaction_id bigint
);


--
-- Name: activity_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE activity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE activity_id_seq OWNED BY activity.id;



--
-- Name: booking; Type: TABLE; Schema: public; 
--

CREATE TABLE booking (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    "recommendationId" bigint,
    "offerId" bigint,
    quantity integer NOT NULL,
    token character varying(6) NOT NULL,
    "userId" bigint NOT NULL
);



--
-- Name: booking_id_seq; Type: SEQUENCE; Schema: public; 
--


CREATE SEQUENCE booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE booking_id_seq OWNED BY booking.id;


--
-- Name: deposit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE deposit (
    id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "userId" bigint NOT NULL,
    source character varying(12) NOT NULL
);


--
-- Name: deposit_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE deposit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: deposit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE deposit_id_seq OWNED BY deposit.id;


--
-- Name: event; Type: TABLE; Schema: public; 
--

CREATE TABLE event (
    "isActive" boolean DEFAULT true NOT NULL,
    "extraData" json,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    type character varying(50),
    name character varying(140) NOT NULL,
    description text,
    conditions character varying(120),
    "ageMin" integer,
    "ageMax" integer,
    accessibility bytea NOT NULL,
    "mediaUrls" character varying(220)[] NOT NULL,
    "durationMinutes" integer NOT NULL,
    "isNational" boolean DEFAULT false NOT NULL,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE event_id_seq OWNED BY event.id;


--
-- Name: event_occurence; Type: TABLE; Schema: public; 
--

CREATE TABLE event_occurence (
    "isActive" boolean DEFAULT true NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    type eventtype,
    "eventId" bigint NOT NULL,
    "venueId" bigint,
    "beginningDatetime" timestamp without time zone NOT NULL,
    "endDatetime" timestamp without time zone NOT NULL,
    accessibility bytea NOT NULL,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: event_occurence_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE event_occurence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: event_occurence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE event_occurence_id_seq OWNED BY event_occurence.id;


--
-- Name: local_provider_event; Type: TABLE; Schema: public; 
--

CREATE TABLE local_provider_event (
    id bigint NOT NULL,
    "providerId" bigint NOT NULL,
    date timestamp without time zone NOT NULL,
    type localprovidereventtype NOT NULL,
    payload character varying(50)
);



--
-- Name: local_provider_event_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE local_provider_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: local_provider_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE local_provider_event_id_seq OWNED BY local_provider_event.id;


--
-- Name: mediation; Type: TABLE; Schema: public; 
--

CREATE TABLE mediation (
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "frontText" text,
    "backText" text,
    "dateCreated" timestamp without time zone NOT NULL,
    "authorId" bigint,
    "offererId" bigint,
    "eventId" bigint,
    "thingId" bigint,
    "tutoIndex" integer,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: mediation_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE mediation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: mediation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE mediation_id_seq OWNED BY mediation.id;


--
-- Name: occasion; Type: TABLE; Schema: public; 
--

CREATE TABLE occasion (
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "thingId" bigint,
    "eventId" bigint,
    "venueId" bigint,
    "lastProviderId" bigint,
    CONSTRAINT check_occasion_has_thing_xor_event CHECK (((("eventId" IS NOT NULL) AND ("thingId" IS NULL)) OR (("eventId" IS NULL) AND ("thingId" IS NOT NULL)))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: occasion_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE occasion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: occasion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE occasion_id_seq OWNED BY occasion.id;


--
-- Name: offer; Type: TABLE; Schema: public; 
--

CREATE TABLE offer (
    "isActive" boolean DEFAULT true NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    "eventOccurenceId" bigint,
    "thingId" bigint,
    "venueId" bigint,
    "offererId" bigint NOT NULL,
    price numeric(10,2) NOT NULL,
    available integer,
    "groupSize" integer NOT NULL,
    "bookingLimitDatetime" timestamp without time zone,
    "bookingRecapSent" timestamp without time zone,
    "lastProviderId" bigint,
    CONSTRAINT check_offer_has_event_occurence_or_thing CHECK ((("eventOccurenceId" IS NOT NULL) OR ("thingId" IS NOT NULL))),
    CONSTRAINT check_offer_has_venue_xor_event_occurence CHECK (((("venueId" IS NOT NULL) AND ("eventOccurenceId" IS NULL)) OR (("venueId" IS NULL) AND ("eventOccurenceId" IS NOT NULL)))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: offer_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE offer_id_seq OWNED BY offer.id;


--
-- Name: offerer; Type: TABLE; Schema: public; 
--

CREATE TABLE offerer (
    "isActive" boolean DEFAULT true NOT NULL,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    address character varying(200) NOT NULL,
    "postalCode" character varying(6) NOT NULL,
    city character varying(50) NOT NULL,
    "validationToken" character varying(27),
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    name character varying(140) NOT NULL,
    siren character varying(9),
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: offerer_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offerer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE offerer_id_seq OWNED BY offerer.id;


--
-- Name: provider; Type: TABLE; Schema: public; 
--

CREATE TABLE provider (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    name character varying(60) NOT NULL,
    "localClass" character varying(30),
    "apiKey" character(32),
    "apiKeyGenerationDate" timestamp without time zone,
    CONSTRAINT check_provider_has_localclass_or_apikey CHECK (((("localClass" IS NOT NULL) AND ("apiKey" IS NULL)) OR (("localClass" IS NULL) AND ("apiKey" IS NOT NULL))))
);



--
-- Name: provider_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE provider_id_seq OWNED BY provider.id;


--
-- Name: recommendation; Type: TABLE; Schema: public; 
--

CREATE TABLE recommendation (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "mediationId" bigint,
    "thingId" bigint,
    "eventId" bigint,
    "shareMedium" character varying(20),
    "inviteforEventOccurenceId" bigint,
    "dateCreated" timestamp without time zone NOT NULL,
    "dateUpdated" timestamp without time zone NOT NULL,
    "dateRead" timestamp without time zone,
    "validUntilDate" timestamp without time zone,
    "isClicked" boolean DEFAULT false NOT NULL,
    "isFavorite" boolean DEFAULT false NOT NULL,
    "isFirst" boolean DEFAULT false NOT NULL,
    CONSTRAINT check_reco_has_thingid_xor_eventid_xor_nothing CHECK (((("thingId" IS NOT NULL) AND ("eventId" IS NULL)) OR (("thingId" IS NULL) AND ("eventId" IS NOT NULL)) OR (("thingId" IS NULL) AND ("eventId" IS NULL))))
);



--
-- Name: recommendation_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE recommendation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: recommendation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE recommendation_id_seq OWNED BY recommendation.id;


--
-- Name: thing; Type: TABLE; Schema: public; 
--

CREATE TABLE thing (
    "isActive" boolean DEFAULT true NOT NULL,
    "extraData" json,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    type character varying(50) NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    "mediaUrls" character varying(120)[] NOT NULL,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thing_book_has_author CHECK ((((type)::text <> 'Book'::text) OR (NOT (("extraData" -> 'author'::text) IS NULL)))),
    CONSTRAINT check_thing_book_has_ean13 CHECK ((((type)::text <> 'Book'::text) OR (("idAtProviders")::text ~ similar_escape('[0-9]{13}'::text, NULL::text)))),
    CONSTRAINT check_thing_book_has_price CHECK ((((type)::text <> 'Book'::text) OR (("extraData" ->> 'prix_livre'::text) ~ similar_escape('[0-9]+(.[0-9]*|)'::text, NULL::text)))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: thing_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE thing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: thing_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE thing_id_seq OWNED BY thing.id;


--
-- Name: user; Type: TABLE; Schema: public; 
--

CREATE TABLE "user" (
    id bigint NOT NULL,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "validationToken" character varying(27),
    email character varying(120) NOT NULL,
    password bytea NOT NULL,
    "publicName" character varying(30) NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "departementCode" character varying(3) NOT NULL,
    "canBook" boolean DEFAULT true NOT NULL,
    "isAdmin" boolean DEFAULT false NOT NULL,
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE user_id_seq OWNED BY "user".id;


--
-- Name: user_offerer; Type: TABLE; Schema: public; 
--

CREATE TABLE user_offerer (
    id bigint NOT NULL,
    "validationToken" character varying(27),
    "userId" bigint NOT NULL,
    "offererId" bigint NOT NULL,
    rights rightstype
);



--
-- Name: user_offerer_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE user_offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_offerer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE user_offerer_id_seq OWNED BY user_offerer.id;


--
-- Name: venue; Type: TABLE; Schema: public; 
--

CREATE TABLE venue (
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    address character varying(200) NOT NULL,
    "postalCode" character varying(6) NOT NULL,
    city character varying(50) NOT NULL,
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    siret character varying(14),
    "departementCode" character varying(3) NOT NULL,
    latitude numeric(8,5),
    longitude numeric(8,5),
    "managingOffererId" bigint NOT NULL,
    "bookingEmail" character varying(120) NOT NULL,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



--
-- Name: venue_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE venue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE venue_id_seq OWNED BY venue.id;


--
-- Name: venue_provider; Type: TABLE; Schema: public; 
--

CREATE TABLE venue_provider (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    "venueId" bigint NOT NULL,
    "providerId" bigint NOT NULL,
    "venueIdAtOfferProvider" character varying(70),
    "lastSyncDate" timestamp without time zone,
    "lastProviderId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: venue_provider_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE venue_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE venue_provider_id_seq OWNED BY venue_provider.id;

--
-- Name: booking id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY booking ALTER COLUMN id SET DEFAULT nextval('booking_id_seq'::regclass);


--
-- Name: deposit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY deposit ALTER COLUMN id SET DEFAULT nextval('deposit_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY event ALTER COLUMN id SET DEFAULT nextval('event_id_seq'::regclass);


--
-- Name: event_occurence id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY event_occurence ALTER COLUMN id SET DEFAULT nextval('event_occurence_id_seq'::regclass);


--
-- Name: local_provider_event id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY local_provider_event ALTER COLUMN id SET DEFAULT nextval('local_provider_event_id_seq'::regclass);


--
-- Name: mediation id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY mediation ALTER COLUMN id SET DEFAULT nextval('mediation_id_seq'::regclass);


--
-- Name: occasion id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY occasion ALTER COLUMN id SET DEFAULT nextval('occasion_id_seq'::regclass);


--
-- Name: offer id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY offer ALTER COLUMN id SET DEFAULT nextval('offer_id_seq'::regclass);


--
-- Name: offerer id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY offerer ALTER COLUMN id SET DEFAULT nextval('offerer_id_seq'::regclass);


--
-- Name: provider id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY provider ALTER COLUMN id SET DEFAULT nextval('provider_id_seq'::regclass);


--
-- Name: recommendation id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY recommendation ALTER COLUMN id SET DEFAULT nextval('recommendation_id_seq'::regclass);


--
-- Name: thing id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY thing ALTER COLUMN id SET DEFAULT nextval('thing_id_seq'::regclass);

--
-- Name: user id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY "user" ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);


--
-- Name: user_offerer id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY user_offerer ALTER COLUMN id SET DEFAULT nextval('user_offerer_id_seq'::regclass);


--
-- Name: venue id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY venue ALTER COLUMN id SET DEFAULT nextval('venue_id_seq'::regclass);


--
-- Name: venue_provider id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY venue_provider ALTER COLUMN id SET DEFAULT nextval('venue_provider_id_seq'::regclass);


--
-- Name: booking booking_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY booking
    ADD CONSTRAINT booking_pkey PRIMARY KEY (id);


--
-- Name: booking booking_token_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY booking
    ADD CONSTRAINT booking_token_key UNIQUE (token);


--
-- Name: deposit deposit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY deposit
    ADD CONSTRAINT deposit_pkey PRIMARY KEY (id);


--
-- Name: event event_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event
    ADD CONSTRAINT "event_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: event_occurence event_occurence_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event_occurence
    ADD CONSTRAINT "event_occurence_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: event_occurence event_occurence_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event_occurence
    ADD CONSTRAINT event_occurence_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: local_provider_event local_provider_event_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY local_provider_event
    ADD CONSTRAINT local_provider_event_pkey PRIMARY KEY (id);


--
-- Name: mediation mediation_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: mediation mediation_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT mediation_pkey PRIMARY KEY (id);


--
-- Name: occasion occasion_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT "occasion_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: occasion occasion_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT occasion_pkey PRIMARY KEY (id);


--
-- Name: offer offer_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: offer offer_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT offer_pkey PRIMARY KEY (id);


--
-- Name: offerer offerer_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offerer
    ADD CONSTRAINT "offerer_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: offerer offerer_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offerer
    ADD CONSTRAINT offerer_pkey PRIMARY KEY (id);


--
-- Name: offerer offerer_siren_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offerer
    ADD CONSTRAINT offerer_siren_key UNIQUE (siren);


--
-- Name: offerer offerer_validationToken_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offerer
    ADD CONSTRAINT "offerer_validationToken_key" UNIQUE ("validationToken");


--
-- Name: provider provider_localClass_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY provider
    ADD CONSTRAINT "provider_localClass_key" UNIQUE ("localClass");


--
-- Name: provider provider_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY provider
    ADD CONSTRAINT provider_pkey PRIMARY KEY (id);


--
-- Name: recommendation recommendation_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT recommendation_pkey PRIMARY KEY (id);


--
-- Name: thing thing_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY thing
    ADD CONSTRAINT "thing_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: thing thing_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY thing
    ADD CONSTRAINT thing_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user_offerer user_offerer_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY user_offerer
    ADD CONSTRAINT user_offerer_pkey PRIMARY KEY (id, "userId", "offererId");


--
-- Name: user_offerer user_offerer_validationToken_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY user_offerer
    ADD CONSTRAINT "user_offerer_validationToken_key" UNIQUE ("validationToken");


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_validationToken_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT "user_validationToken_key" UNIQUE ("validationToken");


--
-- Name: venue venue_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue
    ADD CONSTRAINT "venue_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: venue venue_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue
    ADD CONSTRAINT venue_pkey PRIMARY KEY (id);


--
-- Name: venue_provider venue_provider_idAtProviders_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue_provider
    ADD CONSTRAINT "venue_provider_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: venue_provider venue_provider_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue_provider
    ADD CONSTRAINT venue_provider_pkey PRIMARY KEY (id);


--
-- Name: venue venue_siret_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue
    ADD CONSTRAINT venue_siret_key UNIQUE (siret);

--
-- Name: idx_event_fts; Type: INDEX; Schema: public; 
--

CREATE INDEX idx_event_fts ON event USING gin (to_tsvector('french'::regconfig, (COALESCE(name, ''::character varying))::text));


--
-- Name: idx_offerer_fts; Type: INDEX; Schema: public; 
--

CREATE INDEX idx_offerer_fts ON offerer USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || (COALESCE(address, ''::character varying))::text) || ' '::text) || (COALESCE(siren, ''::character varying))::text)));


--
-- Name: idx_thing_fts; Type: INDEX; Schema: public; 
--

CREATE INDEX idx_thing_fts ON thing USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || COALESCE((("extraData" -> 'author'::text))::text, ''::text)) || ' '::text) || COALESCE((("extraData" -> 'byArtist'::text))::text, ''::text))));


--
-- Name: idx_venue_fts; Type: INDEX; Schema: public; 
--

CREATE INDEX idx_venue_fts ON venue USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || (COALESCE(address, ''::character varying))::text) || ' '::text) || (COALESCE(siret, ''::character varying))::text)));


--
-- Name: ix_booking_offerId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_booking_offerId" ON booking USING btree ("offerId");


--
-- Name: ix_booking_userId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_booking_userId" ON booking USING btree ("userId");


--
-- Name: ix_deposit_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_deposit_userId" ON deposit USING btree ("userId");


--
-- Name: ix_event_occurence_beginningDatetime; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_event_occurence_beginningDatetime" ON event_occurence USING btree ("beginningDatetime");


--
-- Name: ix_event_occurence_eventId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_event_occurence_eventId" ON event_occurence USING btree ("eventId");


--
-- Name: ix_event_occurence_venueId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_event_occurence_venueId" ON event_occurence USING btree ("venueId");


--
-- Name: ix_mediation_eventId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_mediation_eventId" ON mediation USING btree ("eventId");


--
-- Name: ix_mediation_thingId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_mediation_thingId" ON mediation USING btree ("thingId");


--
-- Name: ix_mediation_tutoIndex; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_mediation_tutoIndex" ON mediation USING btree ("tutoIndex");


--
-- Name: ix_occasion_venueId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_occasion_venueId" ON occasion USING btree ("venueId");


--
-- Name: ix_offer_available; Type: INDEX; Schema: public; 
--

CREATE INDEX ix_offer_available ON offer USING btree (available);


--
-- Name: ix_offer_eventOccurenceId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_offer_eventOccurenceId" ON offer USING btree ("eventOccurenceId");


--
-- Name: ix_offer_offererId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_offer_offererId" ON offer USING btree ("offererId");


--
-- Name: ix_offer_thingId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_offer_thingId" ON offer USING btree ("thingId");


--
-- Name: ix_offer_venueId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_offer_venueId" ON offer USING btree ("venueId");


--
-- Name: ix_recommendation_dateRead; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_dateRead" ON recommendation USING btree ("dateRead");


--
-- Name: ix_recommendation_eventId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_eventId" ON recommendation USING btree ("eventId");


--
-- Name: ix_recommendation_mediationId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_mediationId" ON recommendation USING btree ("mediationId");


--
-- Name: ix_recommendation_thingId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_thingId" ON recommendation USING btree ("thingId");


--
-- Name: ix_recommendation_userId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_userId" ON recommendation USING btree ("userId");


--
-- Name: ix_recommendation_validUntilDate; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_recommendation_validUntilDate" ON recommendation USING btree ("validUntilDate");


--
-- Name: ix_venue_departementCode; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_venue_departementCode" ON venue USING btree ("departementCode");


--
-- Name: ix_venue_managingOffererId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_venue_managingOffererId" ON venue USING btree ("managingOffererId");


--
-- Name: ix_venue_provider_venueId; Type: INDEX; Schema: public; 
--

CREATE INDEX "ix_venue_provider_venueId" ON venue_provider USING btree ("venueId");


--
-- Name: booking booking_update; Type: TRIGGER; Schema: public; 
--

CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE ON booking NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE check_booking();


--
-- Name: offer offer_update; Type: TRIGGER; Schema: public; 
--

CREATE CONSTRAINT TRIGGER offer_update AFTER INSERT OR UPDATE ON offer NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE check_offer();

--
-- Name: booking booking_offerId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY booking
    ADD CONSTRAINT "booking_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES offer(id);


--
-- Name: booking booking_recommendationId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY booking
    ADD CONSTRAINT "booking_recommendationId_fkey" FOREIGN KEY ("recommendationId") REFERENCES recommendation(id);


--
-- Name: booking booking_userId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY booking
    ADD CONSTRAINT "booking_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"(id);


--
-- Name: deposit deposit_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY deposit
    ADD CONSTRAINT "deposit_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"(id);


--
-- Name: event event_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event
    ADD CONSTRAINT "event_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: event_occurence event_occurence_eventId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event_occurence
    ADD CONSTRAINT "event_occurence_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES event(id);


--
-- Name: event_occurence event_occurence_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event_occurence
    ADD CONSTRAINT "event_occurence_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: event_occurence event_occurence_venueId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY event_occurence
    ADD CONSTRAINT "event_occurence_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES venue(id);


--
-- Name: local_provider_event local_provider_event_providerId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY local_provider_event
    ADD CONSTRAINT "local_provider_event_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES provider(id);


--
-- Name: mediation mediation_authorId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES "user"(id);


--
-- Name: mediation mediation_eventId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES event(id);


--
-- Name: mediation mediation_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: mediation mediation_offererId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES offerer(id);


--
-- Name: mediation mediation_thingId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY mediation
    ADD CONSTRAINT "mediation_thingId_fkey" FOREIGN KEY ("thingId") REFERENCES thing(id);


--
-- Name: occasion occasion_eventId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT "occasion_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES event(id);


--
-- Name: occasion occasion_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT "occasion_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: occasion occasion_thingId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT "occasion_thingId_fkey" FOREIGN KEY ("thingId") REFERENCES thing(id);


--
-- Name: occasion occasion_venueId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY occasion
    ADD CONSTRAINT "occasion_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES venue(id);


--
-- Name: offer offer_eventOccurenceId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_eventOccurenceId_fkey" FOREIGN KEY ("eventOccurenceId") REFERENCES event_occurence(id);


--
-- Name: offer offer_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: offer offer_offererId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES offerer(id);


--
-- Name: offer offer_thingId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_thingId_fkey" FOREIGN KEY ("thingId") REFERENCES thing(id);


--
-- Name: offer offer_venueId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offer
    ADD CONSTRAINT "offer_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES venue(id);


--
-- Name: offerer offerer_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY offerer
    ADD CONSTRAINT "offerer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: recommendation recommendation_eventId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT "recommendation_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES event(id);


--
-- Name: recommendation recommendation_inviteforEventOccurenceId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT "recommendation_inviteforEventOccurenceId_fkey" FOREIGN KEY ("inviteforEventOccurenceId") REFERENCES event_occurence(id);


--
-- Name: recommendation recommendation_mediationId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT "recommendation_mediationId_fkey" FOREIGN KEY ("mediationId") REFERENCES mediation(id);


--
-- Name: recommendation recommendation_thingId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT "recommendation_thingId_fkey" FOREIGN KEY ("thingId") REFERENCES thing(id);


--
-- Name: recommendation recommendation_userId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY recommendation
    ADD CONSTRAINT "recommendation_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"(id);


--
-- Name: thing thing_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY thing
    ADD CONSTRAINT "thing_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: user_offerer user_offerer_offererId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY user_offerer
    ADD CONSTRAINT "user_offerer_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES offerer(id);


--
-- Name: user_offerer user_offerer_userId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY user_offerer
    ADD CONSTRAINT "user_offerer_userId_fkey" FOREIGN KEY ("userId") REFERENCES "user"(id);


--
-- Name: venue venue_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue
    ADD CONSTRAINT "venue_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: venue venue_managingOffererId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue
    ADD CONSTRAINT "venue_managingOffererId_fkey" FOREIGN KEY ("managingOffererId") REFERENCES offerer(id);


--
-- Name: venue_provider venue_provider_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue_provider
    ADD CONSTRAINT "venue_provider_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES provider(id);


--
-- Name: venue_provider venue_provider_providerId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue_provider
    ADD CONSTRAINT "venue_provider_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES provider(id);


--
-- Name: venue_provider venue_provider_venueId_fkey; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY venue_provider
    ADD CONSTRAINT "venue_provider_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES venue(id);


--
-- PostgreSQL database dump complete
--

