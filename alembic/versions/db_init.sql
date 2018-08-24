--
-- PostgreSQL database dump
--

-- Dumped from database version 10.4 (Debian 10.4-2.pgdg90+1)
-- Dumped by pg_dump version 10.5 (Ubuntu 10.5-1.pgdg16.04+1)

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


CREATE TYPE public.eventtype AS ENUM (
    'BusinessEvent',
    'ChildrensEvent',
    'ComedyEvent',
    'CourseInstance',
    'DanceEvent',
    'DeliveryEvent',
    'EducationEvent',
    'ExhibitionEvent',
    'Festival',
    'FoodEvent',
    'LiteraryEvent',
    'MusicEvent',
    'PublicationEvent',
    'BroadcastEvent',
    'OnDemandEvent',
    'SaleEvent',
    'ScreeningEvent',
    'SocialEvent',
    'SportsEvent',
    'TheaterEvent',
    'VisualArtsEvent'
);



CREATE TYPE public.localprovidereventtype AS ENUM (
    'SyncError',
    'SyncPartStart',
    'SyncPartEnd',
    'SyncStart',
    'SyncEnd'
);



CREATE TYPE public.rightstype AS ENUM (
    'admin',
    'editor'
);



CREATE TYPE public.thingtype AS ENUM (
    'Article',
    'AudioObject',
    'Blog',
    'Book',
    'BookSeries',
    'BroadcastService',
    'BusTrip',
    'CableOrSatelliteService',
    'Clip',
    'Course',
    'CreativeWorkSeason',
    'CreativeWorkSeries',
    'DataDownload',
    'Episode',
    'FoodService',
    'Game',
    'ImageObject',
    'Map',
    'MediaObject',
    'Movie',
    'MovieClip',
    'MovieSeries',
    'MusicAlbum',
    'MusicComposition',
    'MusicRecording',
    'MusicVideoObject',
    'NewsArticle',
    'Painting',
    'PaymentCard',
    'Periodical',
    'Photograph',
    'Product',
    'ProgramMembership',
    'PublicationIssue',
    'PublicationVolume',
    'RadioClip',
    'RadioEpisode',
    'RadioSeason',
    'RadioSeries',
    'Report',
    'ScholarlyArticle',
    'Sculpture',
    'Service',
    'TaxiService',
    'TechArticle',
    'Ticket',
    'TVClip',
    'TVEpisode',
    'TVSeason',
    'TVSeries',
    'VideoGame',
    'VideoGameClip',
    'VideoGameSeries',
    'VideoObject',
    'VisualArtwork'
);




CREATE FUNCTION public.check_booking() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF EXISTS (SELECT "available" FROM stock WHERE id=NEW."stockId" AND "available" IS NOT NULL)
         AND ((SELECT "available" FROM stock WHERE id=NEW."stockId")
              < (SELECT COUNT(*) FROM booking WHERE "stockId"=NEW."stockId")) THEN
          RAISE EXCEPTION 'tooManyBookings'
                USING HINT = 'Number of bookings cannot exceed "stock.available"';
      END IF;
      
      IF (SELECT get_wallet_balance(NEW."userId") < 0)
      THEN RAISE EXCEPTION 'insufficientFunds'
                 USING HINT = 'The user does not have enough credit to book';
      END IF;
      
      RETURN NEW;
    END;
    $$;



CREATE FUNCTION public.check_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF NOT NEW.available IS NULL AND
      ((SELECT COUNT(*) FROM booking WHERE "stockId"=NEW.id) > NEW.available) THEN
        RAISE EXCEPTION 'available_too_low'
              USING HINT = 'stock.available cannot be lower than number of bookings';
      END IF;

      IF NOT NEW."bookingLimitDatetime" IS NULL AND
      (NEW."bookingLimitDatetime" > (SELECT "beginningDatetime" FROM event_occurrence WHERE id=NEW."eventOccurrenceId")) THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'stock.bookingLimitDatetime after event_occurrence.beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$;






CREATE FUNCTION public.get_wallet_balance(user_id bigint) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN 
                (SELECT COALESCE(SUM(amount), 0) FROM deposit WHERE "userId"=user_id)
                -
                (SELECT COALESCE(SUM(amount * quantity), 0) FROM booking WHERE "userId"=user_id);
    END; $$;



CREATE FUNCTION public.jsonb_change_key_name(data jsonb, old_key text, new_key text) RETURNS jsonb
    LANGUAGE sql IMMUTABLE
    AS $$
    SELECT ('{'||string_agg(to_json(CASE WHEN key = old_key THEN new_key ELSE key END)||':'||value, ',')||'}')::jsonb
    FROM (
        SELECT *
        FROM jsonb_each(data)
    ) t;
$$;



CREATE FUNCTION public.jsonb_subtract(arg1 jsonb, arg2 jsonb) RETURNS jsonb
    LANGUAGE sql
    AS $$
SELECT
  COALESCE(json_object_agg(key, value), '{}')::jsonb
FROM
  jsonb_each(arg1)
WHERE
  (arg1 -> key) <> (arg2 -> key) OR (arg2 -> key) IS NULL
$$;



CREATE OPERATOR public.- (
    PROCEDURE = public.jsonb_subtract,
    LEFTARG = jsonb,
    RIGHTARG = jsonb
);



SET default_tablespace = '';

SET default_with_oids = false;


CREATE TABLE public.booking (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    "recommendationId" bigint,
    "stockId" bigint NOT NULL,
    quantity integer NOT NULL,
    token character varying(6) NOT NULL,
    "userId" bigint NOT NULL,
    amount numeric(10,2) NOT NULL
);



CREATE SEQUENCE public.booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.booking_id_seq OWNED BY public.booking.id;


CREATE TABLE public.deposit (
    id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "userId" bigint NOT NULL,
    source character varying(12) NOT NULL
);



CREATE SEQUENCE public.deposit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.deposit_id_seq OWNED BY public.deposit.id;


CREATE TABLE public.event (
    "isActive" boolean DEFAULT true NOT NULL,
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
    "lastProviderId" bigint,
    "isNational" boolean DEFAULT false NOT NULL,
    "extraData" json,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


CREATE TABLE public.event_occurrence (
    "isActive" boolean DEFAULT true NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    type public.eventtype,
    "beginningDatetime" timestamp without time zone NOT NULL,
    accessibility bytea NOT NULL,
    "lastProviderId" bigint,
    "endDatetime" timestamp without time zone NOT NULL,
    "offerId" bigint NOT NULL,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



CREATE SEQUENCE public.event_occurrence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.event_occurrence_id_seq OWNED BY public.event_occurrence.id;


CREATE TABLE public.local_provider_event (
    id bigint NOT NULL,
    "providerId" bigint NOT NULL,
    date timestamp without time zone NOT NULL,
    type public.localprovidereventtype NOT NULL,
    payload character varying(50)
);



CREATE SEQUENCE public.local_provider_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.local_provider_event_id_seq OWNED BY public.local_provider_event.id;


CREATE TABLE public.mediation (
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "frontText" text,
    "backText" text,
    "dateCreated" timestamp without time zone NOT NULL,
    "authorId" bigint,
    "tutoIndex" integer,
    "lastProviderId" bigint,
    "offerId" bigint,
    credit character varying(255),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.mediation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.mediation_id_seq OWNED BY public.mediation.id;


CREATE TABLE public.offer (
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "thingId" bigint,
    "eventId" bigint,
    "venueId" bigint,
    "lastProviderId" bigint,
    CONSTRAINT check_offer_has_thing_xor_event CHECK (((("eventId" IS NOT NULL) AND ("thingId" IS NULL)) OR (("eventId" IS NULL) AND ("thingId" IS NOT NULL)))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



CREATE SEQUENCE public.offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.offer_id_seq OWNED BY public.offer.id;


CREATE TABLE public.offerer (
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    address character varying(200) NOT NULL,
    "lastProviderId" bigint,
    "postalCode" character varying(6) NOT NULL,
    city character varying(50) NOT NULL,
    siren character varying(9),
    "isActive" boolean DEFAULT true NOT NULL,
    "validationToken" character varying(27),
    "dateCreated" timestamp without time zone NOT NULL,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.offerer_id_seq OWNED BY public.offerer.id;


CREATE TABLE public.provider (
    id bigint NOT NULL,
    name character varying(60) NOT NULL,
    "localClass" character varying(30),
    "isActive" boolean DEFAULT true NOT NULL,
    "apiKey" character(32),
    "apiKeyGenerationDate" timestamp without time zone,
    CONSTRAINT check_provider_has_localclass_or_apikey CHECK (((("localClass" IS NOT NULL) AND ("apiKey" IS NULL)) OR (("localClass" IS NULL) AND ("apiKey" IS NOT NULL))))
);



CREATE SEQUENCE public.provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.provider_id_seq OWNED BY public.provider.id;


CREATE TABLE public.recommendation (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "mediationId" bigint,
    "shareMedium" character varying(20),
    "inviteforEventOccurrenceId" bigint,
    "dateCreated" timestamp without time zone NOT NULL,
    "dateUpdated" timestamp without time zone NOT NULL,
    "dateRead" timestamp without time zone,
    "validUntilDate" timestamp without time zone,
    "isClicked" boolean DEFAULT false NOT NULL,
    "isFavorite" boolean DEFAULT false NOT NULL,
    "isFirst" boolean DEFAULT false NOT NULL,
    "offerId" bigint
);



CREATE SEQUENCE public.recommendation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.recommendation_id_seq OWNED BY public.recommendation.id;


CREATE TABLE public.stock (
    "isActive" boolean DEFAULT true NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    "eventOccurrenceId" bigint,
    price numeric(10,2) NOT NULL,
    available integer,
    "groupSize" integer NOT NULL,
    "bookingLimitDatetime" timestamp without time zone,
    "bookingRecapSent" timestamp without time zone,
    "lastProviderId" bigint,
    "offerId" bigint,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_stock_has_event_occurrence_or_offer CHECK ((("eventOccurrenceId" IS NOT NULL) OR ("offerId" IS NOT NULL)))
);



CREATE SEQUENCE public.stock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.stock_id_seq OWNED BY public.stock.id;


CREATE TABLE public.thing (
    "isActive" boolean DEFAULT true NOT NULL,
    "extraData" json,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    "mediaUrls" character varying(120)[] NOT NULL,
    "lastProviderId" bigint,
    type character varying(50) NOT NULL,
    url character varying(255),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.thing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.thing_id_seq OWNED BY public.thing.id;


CREATE TABLE public.transaction (
    id bigint NOT NULL,
    native_transaction_id bigint,
    issued_at timestamp without time zone,
    client_addr inet,
    actor_id bigint
);



CREATE SEQUENCE public.transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.transaction_id_seq OWNED BY public.transaction.id;


CREATE TABLE public."user" (
    id bigint NOT NULL,
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    email character varying(120) NOT NULL,
    password bytea NOT NULL,
    "publicName" character varying(30) NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "departementCode" character varying(3) NOT NULL,
    "canBookFreeOffers" boolean DEFAULT true NOT NULL,
    "isAdmin" boolean DEFAULT false NOT NULL,
    "validationToken" character varying(27),
    CONSTRAINT check_admin_cannot_book_free_offers CHECK (((("canBookFreeOffers" IS FALSE) AND ("isAdmin" IS TRUE)) OR ("isAdmin" IS FALSE))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


CREATE TABLE public.user_offerer (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "offererId" bigint NOT NULL,
    rights public.rightstype,
    "validationToken" character varying(27)
);



CREATE SEQUENCE public.user_offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.user_offerer_id_seq OWNED BY public.user_offerer.id;


CREATE TABLE public.venue (
    "thumbCount" integer NOT NULL,
    "firstThumbDominantColor" bytea,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    address character varying(200),
    latitude numeric(8,5),
    longitude numeric(8,5),
    "lastProviderId" bigint,
    "departementCode" character varying(3),
    "postalCode" character varying(6),
    city character varying(50),
    siret character varying(14),
    "managingOffererId" bigint NOT NULL,
    "bookingEmail" character varying(120) NOT NULL,
    "isVirtual" boolean DEFAULT false NOT NULL,
    CONSTRAINT check_is_virtual_xor_has_address CHECK (((("isVirtual" IS TRUE) AND ((address IS NULL) AND ("postalCode" IS NULL) AND (city IS NULL) AND ("departementCode" IS NULL))) OR (("isVirtual" IS FALSE) AND ((address IS NOT NULL) AND ("postalCode" IS NOT NULL) AND (city IS NOT NULL) AND ("departementCode" IS NOT NULL))))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT check_thumb_has_dominant_color CHECK ((("thumbCount" = 0) OR ("firstThumbDominantColor" IS NOT NULL)))
);



CREATE SEQUENCE public.venue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.venue_id_seq OWNED BY public.venue.id;


CREATE TABLE public.venue_provider (
    id bigint NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    "providerId" bigint NOT NULL,
    "venueIdAtOfferProvider" character varying(70),
    "lastProviderId" bigint,
    "venueId" bigint NOT NULL,
    "lastSyncDate" timestamp without time zone,
    "isActive" boolean DEFAULT true NOT NULL,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



CREATE SEQUENCE public.venue_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public.venue_provider_id_seq OWNED BY public.venue_provider.id;



ALTER TABLE ONLY public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq'::regclass);


ALTER TABLE ONLY public.deposit ALTER COLUMN id SET DEFAULT nextval('public.deposit_id_seq'::regclass);


ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


ALTER TABLE ONLY public.event_occurrence ALTER COLUMN id SET DEFAULT nextval('public.event_occurrence_id_seq'::regclass);


ALTER TABLE ONLY public.local_provider_event ALTER COLUMN id SET DEFAULT nextval('public.local_provider_event_id_seq'::regclass);


ALTER TABLE ONLY public.mediation ALTER COLUMN id SET DEFAULT nextval('public.mediation_id_seq'::regclass);


ALTER TABLE ONLY public.offer ALTER COLUMN id SET DEFAULT nextval('public.offer_id_seq'::regclass);


ALTER TABLE ONLY public.offerer ALTER COLUMN id SET DEFAULT nextval('public.offerer_id_seq'::regclass);


ALTER TABLE ONLY public.provider ALTER COLUMN id SET DEFAULT nextval('public.provider_id_seq'::regclass);


ALTER TABLE ONLY public.recommendation ALTER COLUMN id SET DEFAULT nextval('public.recommendation_id_seq'::regclass);


ALTER TABLE ONLY public.stock ALTER COLUMN id SET DEFAULT nextval('public.stock_id_seq'::regclass);


ALTER TABLE ONLY public.thing ALTER COLUMN id SET DEFAULT nextval('public.thing_id_seq'::regclass);


ALTER TABLE ONLY public.transaction ALTER COLUMN id SET DEFAULT nextval('public.transaction_id_seq'::regclass);


ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


ALTER TABLE ONLY public.user_offerer ALTER COLUMN id SET DEFAULT nextval('public.user_offerer_id_seq'::regclass);


ALTER TABLE ONLY public.venue ALTER COLUMN id SET DEFAULT nextval('public.venue_id_seq'::regclass);


ALTER TABLE ONLY public.venue_provider ALTER COLUMN id SET DEFAULT nextval('public.venue_provider_id_seq'::regclass);


ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_token_key UNIQUE (token);


ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT deposit_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.event
    ADD CONSTRAINT "event_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.event_occurrence
    ADD CONSTRAINT "event_occurrence_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.event_occurrence
    ADD CONSTRAINT event_occurrence_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.local_provider_event
    ADD CONSTRAINT local_provider_event_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT mediation_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT offerer_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT offerer_siren_key UNIQUE (siren);


ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "offerer_validationToken_key" UNIQUE ("validationToken");


ALTER TABLE ONLY public.provider
    ADD CONSTRAINT "provider_localClass_key" UNIQUE ("localClass");


ALTER TABLE ONLY public.provider
    ADD CONSTRAINT provider_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.recommendation
    ADD CONSTRAINT recommendation_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.stock
    ADD CONSTRAINT stock_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.thing
    ADD CONSTRAINT "thing_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.thing
    ADD CONSTRAINT thing_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.transaction
    ADD CONSTRAINT transaction_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT user_offerer_pkey PRIMARY KEY (id, "userId", "offererId");


ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_offerer_validationToken_key" UNIQUE ("validationToken");


ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_validationToken_key" UNIQUE ("validationToken");


ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.venue
    ADD CONSTRAINT venue_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_idAtProviders_key" UNIQUE ("idAtProviders");


ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT venue_provider_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.venue
    ADD CONSTRAINT venue_siret_key UNIQUE (siret);




CREATE INDEX idx_event_fts ON public.event USING gin (to_tsvector('french'::regconfig, (COALESCE(name, ''::character varying))::text));


CREATE INDEX idx_offerer_fts ON public.offerer USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || (COALESCE(address, ''::character varying))::text) || ' '::text) || (COALESCE(siren, ''::character varying))::text)));


CREATE INDEX idx_thing_fts ON public.thing USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || COALESCE((("extraData" -> 'author'::text))::text, ''::text)) || ' '::text) || COALESCE((("extraData" -> 'byArtist'::text))::text, ''::text))));


CREATE INDEX idx_venue_fts ON public.venue USING gin (to_tsvector('french'::regconfig, (((((COALESCE(name, ''::character varying))::text || ' '::text) || (COALESCE(address, ''::character varying))::text) || ' '::text) || (COALESCE(siret, ''::character varying))::text)));


CREATE INDEX "ix_booking_stockId" ON public.booking USING btree ("stockId");


CREATE INDEX "ix_booking_userId" ON public.booking USING btree ("userId");


CREATE INDEX "ix_deposit_userId" ON public.deposit USING btree ("userId");


CREATE INDEX "ix_event_occurrence_beginningDatetime" ON public.event_occurrence USING btree ("beginningDatetime");


CREATE INDEX "ix_event_occurrence_offerId" ON public.event_occurrence USING btree ("offerId");


CREATE INDEX "ix_mediation_offerId" ON public.mediation USING btree ("offerId");


CREATE INDEX "ix_mediation_tutoIndex" ON public.mediation USING btree ("tutoIndex");


CREATE INDEX "ix_offer_venueId" ON public.offer USING btree ("venueId");


CREATE INDEX "ix_recommendation_dateRead" ON public.recommendation USING btree ("dateRead");


CREATE INDEX "ix_recommendation_mediationId" ON public.recommendation USING btree ("mediationId");


CREATE INDEX "ix_recommendation_offerId" ON public.recommendation USING btree ("offerId");


CREATE INDEX "ix_recommendation_userId" ON public.recommendation USING btree ("userId");


CREATE INDEX "ix_recommendation_validUntilDate" ON public.recommendation USING btree ("validUntilDate");


CREATE INDEX ix_stock_available ON public.stock USING btree (available);


CREATE INDEX "ix_stock_eventOccurrenceId" ON public.stock USING btree ("eventOccurrenceId");


CREATE INDEX "ix_stock_offerId" ON public.stock USING btree ("offerId");


CREATE INDEX ix_transaction_native_transaction_id ON public.transaction USING btree (native_transaction_id);


CREATE INDEX "ix_venue_departementCode" ON public.venue USING btree ("departementCode");


CREATE INDEX "ix_venue_managingOffererId" ON public.venue USING btree ("managingOffererId");


CREATE INDEX "ix_venue_provider_venueId" ON public.venue_provider USING btree ("venueId");



CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE ON public.booking NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE public.check_booking();


CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE ON public.stock NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE PROCEDURE public.check_stock();



ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_recommendationId_fkey" FOREIGN KEY ("recommendationId") REFERENCES public.recommendation(id);


ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_stockId_fkey" FOREIGN KEY ("stockId") REFERENCES public.stock(id);


ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT "deposit_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


ALTER TABLE ONLY public.event
    ADD CONSTRAINT "event_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.event_occurrence
    ADD CONSTRAINT "event_occurrence_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.event_occurrence
    ADD CONSTRAINT "event_occurrence_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


ALTER TABLE ONLY public.local_provider_event
    ADD CONSTRAINT "local_provider_event_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES public."user"(id);


ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_eventId_fkey" FOREIGN KEY ("eventId") REFERENCES public.event(id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_thingId_fkey" FOREIGN KEY ("thingId") REFERENCES public.thing(id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.recommendation
    ADD CONSTRAINT "recommendation_inviteforEventOccurrenceId_fkey" FOREIGN KEY ("inviteforEventOccurrenceId") REFERENCES public.event_occurrence(id);


ALTER TABLE ONLY public.recommendation
    ADD CONSTRAINT "recommendation_mediationId_fkey" FOREIGN KEY ("mediationId") REFERENCES public.mediation(id);


ALTER TABLE ONLY public.recommendation
    ADD CONSTRAINT "recommendation_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


ALTER TABLE ONLY public.recommendation
    ADD CONSTRAINT "recommendation_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_eventOccurrenceId_fkey" FOREIGN KEY ("eventOccurrenceId") REFERENCES public.event_occurrence(id);


ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


ALTER TABLE ONLY public.thing
    ADD CONSTRAINT "thing_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT "user_offerer_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT "user_offerer_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_managingOffererId_fkey" FOREIGN KEY ("managingOffererId") REFERENCES public.offerer(id);


ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES public.provider(id);


ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgresql
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

