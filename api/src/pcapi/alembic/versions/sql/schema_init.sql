--
-- PostgreSQL database dump
--

-- Dumped from database version 12.9
-- Dumped by pg_dump version 12.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: pass_culture
--

CREATE SCHEMA tiger;



--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: pass_culture
--

CREATE SCHEMA tiger_data;



--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: pass_culture
--

CREATE SCHEMA topology;



--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: pass_culture
--

COMMENT ON SCHEMA topology IS 'PostGIS Topology schema';


--
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- Name: booking_status; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.booking_status AS ENUM (
    'PENDING',
    'CONFIRMED',
    'USED',
    'CANCELLED',
    'REIMBURSED'
);



--
-- Name: bookingcancellationreasons; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.bookingcancellationreasons AS ENUM (
    'OFFERER',
    'BENEFICIARY',
    'EXPIRED',
    'FRAUD',
    'REFUSED_BY_INSTITUTE'
);



--
-- Name: bookingstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.bookingstatus AS ENUM (
    'PENDING',
    'CONFIRMED',
    'USED',
    'CANCELLED',
    'REIMBURSED'
);



--
-- Name: cancellation_reason; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.cancellation_reason AS ENUM (
    'OFFERER',
    'BENEFICIARY',
    'EXPIRED',
    'FRAUD',
    'REFUSED_BY_INSTITUTE'
);



--
-- Name: eventtype; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.eventtype AS ENUM (
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
-- Name: featuretoggle; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.featuretoggle AS ENUM (
    'SEARCH_ALGOLIA',
    'SYNCHRONIZE_ALGOLIA',
    'SYNCHRONIZE_ALLOCINE',
    'SYNCHRONIZE_TITELIVE_PRODUCTS',
    'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
    'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
    'UPDATE_BOOKING_USED',
    'BOOKINGS_V2',
    'API_SIRENE_AVAILABLE'
);



--
-- Name: importstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.importstatus AS ENUM (
    'DUPLICATE',
    'CREATED',
    'ERROR',
    'REJECTED',
    'RETRY',
    'DRAFT',
    'ONGOING',
    'WITHOUT_CONTINUATION'
);



--
-- Name: localprovidereventtype; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.localprovidereventtype AS ENUM (
    'SyncError',
    'SyncPartStart',
    'SyncPartEnd',
    'SyncStart',
    'SyncEnd'
);



--
-- Name: ministry; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.ministry AS ENUM (
    'EDUCATION_NATIONALE',
    'MER',
    'AGRICULTURE',
    'ARMEES'
);



--
-- Name: pricerule; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.pricerule AS ENUM (
    'default'
);



--
-- Name: status; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.status AS ENUM (
    'ACCEPTED',
    'REJECTED',
    'DRAFT'
);



--
-- Name: studentlevels; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.studentlevels AS ENUM (
    'COLLEGE4',
    'COLLEGE3',
    'CAP1',
    'CAP2',
    'GENERAL2',
    'GENERAL1',
    'GENERAL0'
);



--
-- Name: transactionstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.transactionstatus AS ENUM (
    'PENDING',
    'NOT_PROCESSABLE',
    'SENT',
    'ERROR',
    'RETRY',
    'BANNED',
    'UNDER_REVIEW'
);



--
-- Name: validation_status; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.validation_status AS ENUM (
    'APPROVED',
    'PENDING',
    'REJECTED',
    'DRAFT'
);



--
-- Name: validation_type; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.validation_type AS ENUM (
    'AUTO',
    'MANUAL',
    'CGU_INCOMPATIBLE_PRODUCT'
);



--
-- Name: validationstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.validationstatus AS ENUM (
    'NEW',
    'PENDING',
    'VALIDATED',
    'REJECTED'
);



--
-- Name: audit_table(regclass); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.audit_table(target_table regclass) RETURNS void
    LANGUAGE sql
    AS $$
SELECT public.audit_table(target_table, ARRAY[]::text[]);
$$;



--
-- Name: audit_table(regclass, text[]); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.audit_table(target_table regclass, ignored_cols text[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    query text;
    excluded_columns_text text = '';
BEGIN
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_insert ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_update ON ' || target_table;
    EXECUTE 'DROP TRIGGER IF EXISTS audit_trigger_delete ON ' || target_table;

    IF array_length(ignored_cols, 1) > 0 THEN
        excluded_columns_text = ', ' || quote_literal(ignored_cols);
    END IF;
    query = 'CREATE TRIGGER audit_trigger_insert AFTER INSERT ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE public.create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_update AFTER UPDATE ON ' ||
             target_table || ' REFERENCING NEW TABLE AS new_table OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE public.create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
    query = 'CREATE TRIGGER audit_trigger_delete AFTER DELETE ON ' ||
             target_table || ' REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT ' ||
             E'WHEN (current_setting(\'session_replication_role\') ' ||
             E'<> \'local\')' ||
             ' EXECUTE PROCEDURE public.create_activity(' ||
             excluded_columns_text ||
             ');';
    RAISE NOTICE '%', query;
    EXECUTE query;
END;
$$;



--
-- Name: check_booking(); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.check_booking() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        lastStockUpdate date := (SELECT "dateModified" FROM stock WHERE id=NEW."stockId");
        deposit_id bigint := (SELECT individual_booking."depositId" FROM booking LEFT JOIN individual_booking ON individual_booking.id = booking."individualBookingId" WHERE booking.id=NEW.id);
    BEGIN
    IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
        AND (
            (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
            <
            (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND status != 'CANCELLED')
            )
        THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
    END IF;

    IF (
        (NEW."individualBookingId" IS NOT NULL OR OLD."individualBookingId" IS NOT NULL)
        AND (
        -- If this is a new booking, we probably want to check the wallet.
        OLD IS NULL
        -- If we're updating an existing booking...
        OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking. (Users with no credits left
            -- should be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.)
            OR (NEW.status != OLD.status AND OLD.status = 'CANCELLED' AND NEW.status != 'CANCELLED')
        )
        )
        AND (
            -- Allow to book free offers even with no credit left (or expired deposits)
            (deposit_id IS NULL AND NEW."amount" != 0)
            OR (deposit_id IS NOT NULL AND get_deposit_balance(deposit_id, false) < 0)
        )
    )
    THEN RAISE EXCEPTION 'insufficientFunds'
                USING HINT = 'The user does not have enough credit to book';
    END IF;

    RETURN NEW;
    END;
    $$;



--
-- Name: check_stock(); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.check_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
      IF
       NOT NEW.quantity IS NULL
       AND
        (
         (
          SELECT SUM(booking.quantity)
          FROM booking
          WHERE "stockId"=NEW.id
          AND NOT booking.status = 'CANCELLED'
         ) > NEW.quantity
        )
      THEN
       RAISE EXCEPTION 'quantity_too_low'
       USING HINT = 'stock.quantity cannot be lower than number of bookings';
      END IF;

      IF NEW."bookingLimitDatetime" IS NOT NULL AND
        NEW."beginningDatetime" IS NOT NULL AND
         NEW."bookingLimitDatetime" > NEW."beginningDatetime" THEN

      RAISE EXCEPTION 'bookingLimitDatetime_too_late'
      USING HINT = 'bookingLimitDatetime after beginningDatetime';
      END IF;

      RETURN NEW;
    END;
    $$;



--
-- Name: event_is_in_less_than_10_days(bigint); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.event_is_in_less_than_10_days(offer_id bigint) RETURNS SETOF integer
    LANGUAGE plpgsql
    AS $$
        BEGIN
           RETURN QUERY
           SELECT 1
            FROM stock
            WHERE stock."offerId" = offer_id
              AND (stock."beginningDatetime" IS NULL
                    OR stock."beginningDatetime" > NOW()
                   AND stock."beginningDatetime" < NOW() + INTERVAL '10 DAY');
        END
        $$;



--
-- Name: get_active_offers_ids(boolean); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.get_active_offers_ids(with_mediation boolean) RETURNS SETOF bigint
    LANGUAGE plpgsql
    AS $$
        BEGIN
            RETURN QUERY
            SELECT DISTINCT ON (offer.id) offer.id
            FROM offer
            JOIN venue ON offer."venueId" = venue.id
            JOIN offerer ON offerer.id = venue."managingOffererId"
            WHERE offer."isActive" = TRUE
                AND venue."validationToken" IS NULL
                AND (
                    NOT with_mediation
                    OR (with_mediation AND EXISTS (SELECT * FROM offer_has_at_least_one_active_mediation(offer.id)))
                )
                AND (EXISTS (SELECT * FROM offer_has_at_least_one_bookable_stock(offer.id)))
                AND offerer."isActive" = TRUE
                AND offerer."validationToken" IS NULL
                AND offer.type != 'ThingType.ACTIVATION'
                AND offer.type != 'EventType.ACTIVATION';
        END;
        $$;



--
-- Name: get_deposit_balance(bigint, boolean); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.get_deposit_balance(deposit_id bigint, only_used_bookings boolean) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
    DECLARE
        deposit_amount bigint := (SELECT CASE WHEN "expirationDate" > now() THEN amount ELSE 0 END amount FROM deposit WHERE id = deposit_id);
        sum_bookings numeric;
    BEGIN
        IF deposit_amount IS NULL
        THEN RAISE EXCEPTION 'the deposit was not found';
        END IF;

        SELECT
            COALESCE(SUM(amount * quantity), 0) INTO sum_bookings
        FROM
            booking
            JOIN individual_booking ON (booking."individualBookingId" = individual_booking.id)
        WHERE
            individual_booking."depositId" = deposit_id
            AND NOT booking.status = 'CANCELLED'
            AND (NOT only_used_bookings OR booking.status in ('USED', 'REIMBURSED'));
        RETURN
            deposit_amount - sum_bookings;
        END;
    $$;



--
-- Name: get_offer_score(bigint); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.get_offer_score(offer_id bigint) RETURNS SETOF bigint
    LANGUAGE plpgsql
    AS $$
                BEGIN
                   RETURN QUERY
                   SELECT coalesce(sum(criterion."scoreDelta"), 0)
                    FROM criterion, offer_criterion
                   WHERE criterion.id = offer_criterion."criterionId"
                     AND offer_criterion."offerId" = offer_id;
                END
                $$;



--
-- Name: get_wallet_balance(bigint, boolean); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.get_wallet_balance(user_id bigint, only_used_bookings boolean) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
    DECLARE
        deposit_id bigint := (SELECT deposit.id FROM deposit WHERE "userId" = user_id  AND "expirationDate" > now());
    BEGIN
        RETURN
            CASE WHEN deposit_id IS NOT NULL THEN get_deposit_balance(deposit_id, only_used_bookings) ELSE 0 END;
    END;
    $$;



--
-- Name: jsonb_change_key_name(jsonb, text, text); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.jsonb_change_key_name(data jsonb, old_key text, new_key text) RETURNS jsonb
    LANGUAGE sql IMMUTABLE
    AS $$
    SELECT ('{'||string_agg(to_json(CASE WHEN key = old_key THEN new_key ELSE key END)||':'||value, ',')||'}')::jsonb
    FROM (
        SELECT *
        FROM jsonb_each(data)
    ) t;
$$;



--
-- Name: jsonb_subtract(jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: pass_culture
--

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



--
-- Name: offer_has_at_least_one_active_mediation(bigint); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.offer_has_at_least_one_active_mediation(offer_id bigint) RETURNS SETOF integer
    LANGUAGE plpgsql
    AS $$
                BEGIN
                   RETURN QUERY
                   SELECT 1
                       FROM mediation
                      WHERE mediation."offerId" = offer_id
                        AND mediation."isActive";
                END
                $$;



--
-- Name: offer_has_at_least_one_bookable_stock(bigint); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.offer_has_at_least_one_bookable_stock(offer_id bigint) RETURNS SETOF integer
    LANGUAGE plpgsql
    AS $$
        BEGIN
           RETURN QUERY
           SELECT 1
              FROM stock
             WHERE stock."offerId" = offer_id
               AND stock."isSoftDeleted" = FALSE
               AND (stock."beginningDatetime" > NOW()
                    OR stock."beginningDatetime" IS NULL)
               AND (stock."bookingLimitDatetime" > NOW()
                    OR stock."bookingLimitDatetime" IS NULL)
               AND (stock.quantity IS NULL
                    OR (SELECT greatest(stock.quantity - COALESCE(sum(booking.quantity), 0),0)
                          FROM booking
                         WHERE booking."stockId" = stock.id
                           AND booking."isCancelled" = FALSE
                        ) > 0
                    );
        END
        $$;



--
-- Name: save_cancellation_date(); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.save_cancellation_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
      IF NEW.status = 'CANCELLED' AND OLD."cancellationDate" IS NULL AND NEW."cancellationDate" IS NULL THEN
          NEW."cancellationDate" = NOW();
      ELSIF NEW.status != 'CANCELLED' THEN
          NEW."cancellationDate" = NULL;
      END IF;
      RETURN NEW;
  END;
  $$;



--
-- Name: save_stock_modification_date(); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.save_stock_modification_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
          IF NEW.quantity != OLD.quantity THEN
            NEW."dateModified" = NOW();
          END IF;
          RETURN NEW;
        END;
        $$;



--
-- Name: -; Type: OPERATOR; Schema: public; Owner: pass_culture
--

CREATE OPERATOR public.- (
    FUNCTION = public.jsonb_subtract,
    LEFTARG = jsonb,
    RIGHTARG = jsonb
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_history; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.action_history (
    id bigint NOT NULL,
    "jsonData" jsonb,
    "actionType" text NOT NULL,
    "actionDate" timestamp without time zone DEFAULT now(),
    "authorUserId" bigint,
    "userId" bigint,
    "offererId" bigint,
    "venueId" bigint,
    comment text,
    CONSTRAINT check_at_least_one_resource CHECK ((num_nonnulls("userId", "offererId", "venueId") >= 1))
);



--
-- Name: action_history_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.action_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: action_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.action_history_id_seq OWNED BY public.action_history.id;


--
-- Name: activation_code; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.activation_code (
    id bigint NOT NULL,
    code text NOT NULL,
    "expirationDate" timestamp without time zone,
    "stockId" bigint NOT NULL,
    "bookingId" bigint
);



--
-- Name: activation_code_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.activation_code_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: activation_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.activation_code_id_seq OWNED BY public.activation_code.id;


--
-- Name: activity; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.activity (
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

CREATE SEQUENCE public.activity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: activity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.activity_id_seq OWNED BY public.activity.id;


--
-- Name: allocine_pivot; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.allocine_pivot (
    id bigint NOT NULL,
    "theaterId" character varying(20) NOT NULL,
    "internalId" text NOT NULL,
    "venueId" bigint NOT NULL
);



--
-- Name: allocine_pivot_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.allocine_pivot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: allocine_pivot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.allocine_pivot_id_seq OWNED BY public.allocine_pivot.id;


--
-- Name: allocine_theater; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.allocine_theater (
    id bigint NOT NULL,
    siret character varying(14),
    "theaterId" character varying(20) NOT NULL,
    "internalId" text NOT NULL
);



--
-- Name: allocine_theater_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.allocine_theater_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: allocine_theater_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.allocine_theater_id_seq OWNED BY public.allocine_theater.id;


--
-- Name: allocine_venue_provider; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.allocine_venue_provider (
    id bigint NOT NULL,
    "isDuo" boolean DEFAULT true NOT NULL,
    quantity integer,
    "internalId" text NOT NULL
);



--
-- Name: allocine_venue_provider_price_rule; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.allocine_venue_provider_price_rule (
    id bigint NOT NULL,
    "allocineVenueProviderId" bigint NOT NULL,
    "priceRule" public.pricerule NOT NULL,
    price numeric(10,2) NOT NULL,
    CONSTRAINT check_price_is_not_negative CHECK ((price >= (0)::numeric))
);



--
-- Name: allocine_venue_provider_price_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.allocine_venue_provider_price_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: allocine_venue_provider_price_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.allocine_venue_provider_price_rule_id_seq OWNED BY public.allocine_venue_provider_price_rule.id;


--
-- Name: api_key; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.api_key (
    id bigint NOT NULL,
    "offererId" bigint NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    prefix text,
    secret bytea
);



--
-- Name: api_key_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.api_key_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: api_key_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.api_key_id_seq OWNED BY public.api_key.id;


--
-- Name: backoffice_user_profile; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.backoffice_user_profile (
    id bigint NOT NULL,
    "userId" bigint NOT NULL
);



--
-- Name: backoffice_user_profile_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.backoffice_user_profile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: backoffice_user_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.backoffice_user_profile_id_seq OWNED BY public.backoffice_user_profile.id;


--
-- Name: bank_information; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.bank_information (
    id bigint NOT NULL,
    "offererId" bigint,
    "venueId" bigint,
    iban character varying(27),
    bic character varying(11),
    "applicationId" integer,
    "dateModified" timestamp without time zone,
    status public.status NOT NULL
);



--
-- Name: bank_information_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.bank_information_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: bank_information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.bank_information_id_seq OWNED BY public.bank_information.id;


--
-- Name: beneficiary_fraud_check; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.beneficiary_fraud_check (
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    "userId" bigint NOT NULL,
    type text NOT NULL,
    "thirdPartyId" text NOT NULL,
    "resultContent" jsonb,
    reason text,
    "reasonCodes" text[],
    status text,
    "eligibilityType" text,
    "idPicturesStored" boolean,
    "updatedAt" timestamp without time zone
);



--
-- Name: beneficiary_fraud_check_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.beneficiary_fraud_check_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: beneficiary_fraud_check_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.beneficiary_fraud_check_id_seq OWNED BY public.beneficiary_fraud_check.id;


--
-- Name: beneficiary_fraud_review; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.beneficiary_fraud_review (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "authorId" bigint NOT NULL,
    review text,
    "dateReviewed" timestamp without time zone DEFAULT now() NOT NULL,
    reason text
);



--
-- Name: beneficiary_fraud_review_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.beneficiary_fraud_review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: beneficiary_fraud_review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.beneficiary_fraud_review_id_seq OWNED BY public.beneficiary_fraud_review.id;


--
-- Name: beneficiary_import; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.beneficiary_import (
    id bigint NOT NULL,
    "beneficiaryId" bigint,
    "applicationId" bigint,
    "sourceId" integer,
    source character varying(255) NOT NULL,
    "eligibilityType" text DEFAULT 'AGE18'::text NOT NULL,
    "thirdPartyId" text
);



--
-- Name: beneficiary_import_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.beneficiary_import_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: beneficiary_import_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.beneficiary_import_id_seq OWNED BY public.beneficiary_import.id;


--
-- Name: beneficiary_import_status; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.beneficiary_import_status (
    id bigint NOT NULL,
    status public.importstatus NOT NULL,
    date timestamp without time zone DEFAULT now() NOT NULL,
    detail character varying(255),
    "beneficiaryImportId" bigint NOT NULL,
    "authorId" bigint
);



--
-- Name: beneficiary_import_status_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.beneficiary_import_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: beneficiary_import_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.beneficiary_import_status_id_seq OWNED BY public.beneficiary_import_status.id;


--
-- Name: book_macro_section; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.book_macro_section (
    id bigint NOT NULL,
    "macroSection" text NOT NULL,
    section text NOT NULL
);



--
-- Name: book_macro_section_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.book_macro_section_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: book_macro_section_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.book_macro_section_id_seq OWNED BY public.book_macro_section.id;


--
-- Name: booking; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.booking (
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "stockId" bigint NOT NULL,
    quantity integer NOT NULL,
    token character varying(6) NOT NULL,
    "userId" bigint,
    amount numeric(10,2) NOT NULL,
    "dateUsed" timestamp without time zone,
    "cancellationDate" timestamp without time zone,
    "cancellationLimitDate" timestamp without time zone,
    "cancellationReason" public.cancellation_reason,
    "displayAsEnded" boolean,
    status public.booking_status NOT NULL,
    "offererId" bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "individualBookingId" bigint,
    "reimbursementDate" timestamp without time zone
);



--
-- Name: booking_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.booking_id_seq OWNED BY public.booking.id;


--
-- Name: boost_cinema_details; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.boost_cinema_details (
    id bigint NOT NULL,
    "cinemaProviderPivotId" bigint,
    "cinemaUrl" text NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    token text,
    "tokenExpirationDate" timestamp without time zone
);



--
-- Name: boost_cinema_details_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.boost_cinema_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: boost_cinema_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.boost_cinema_details_id_seq OWNED BY public.boost_cinema_details.id;


--
-- Name: business_unit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.business_unit (
    id bigint NOT NULL,
    name text,
    siret character varying(14),
    "bankAccountId" bigint,
    "cashflowFrequency" text NOT NULL,
    "invoiceFrequency" text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL
);



--
-- Name: business_unit_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.business_unit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: business_unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.business_unit_id_seq OWNED BY public.business_unit.id;


--
-- Name: business_unit_venue_link; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.business_unit_venue_link (
    id bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "businessUnitId" bigint NOT NULL,
    timespan tsrange NOT NULL
);



--
-- Name: business_unit_venue_link_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.business_unit_venue_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: business_unit_venue_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.business_unit_venue_link_id_seq OWNED BY public.business_unit_venue_link.id;


--
-- Name: cashflow; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cashflow (
    id bigint NOT NULL,
    "creationDate" timestamp without time zone DEFAULT now() NOT NULL,
    status text NOT NULL,
    "bankAccountId" bigint NOT NULL,
    "batchId" bigint NOT NULL,
    amount integer NOT NULL,
    "transactionId" uuid DEFAULT public.gen_random_uuid() NOT NULL,
    "businessUnitId" bigint,
    "reimbursementPointId" bigint,
    CONSTRAINT non_zero_amount_check CHECK ((amount <> 0))
);



--
-- Name: cashflow_batch; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cashflow_batch (
    id bigint NOT NULL,
    "creationDate" timestamp without time zone DEFAULT now() NOT NULL,
    cutoff timestamp without time zone NOT NULL,
    label text NOT NULL
);



--
-- Name: cashflow_batch_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.cashflow_batch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cashflow_batch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.cashflow_batch_id_seq OWNED BY public.cashflow_batch.id;


--
-- Name: cashflow_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.cashflow_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cashflow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.cashflow_id_seq OWNED BY public.cashflow.id;


--
-- Name: cashflow_log; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cashflow_log (
    id bigint NOT NULL,
    "cashflowId" bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "statusBefore" text NOT NULL,
    "statusAfter" text NOT NULL,
    details jsonb DEFAULT '{}'::jsonb
);



--
-- Name: cashflow_log_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.cashflow_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cashflow_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.cashflow_log_id_seq OWNED BY public.cashflow_log.id;


--
-- Name: cashflow_pricing; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cashflow_pricing (
    "cashflowId" bigint NOT NULL,
    "pricingId" bigint NOT NULL
);



--
-- Name: cds_cinema_details; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cds_cinema_details (
    id bigint NOT NULL,
    "cinemaProviderPivotId" bigint,
    "cinemaApiToken" text NOT NULL,
    "accountId" text NOT NULL
);



--
-- Name: cds_cinema_details_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.cds_cinema_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cds_cinema_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.cds_cinema_details_id_seq OWNED BY public.cds_cinema_details.id;


--
-- Name: cinema_provider_pivot; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.cinema_provider_pivot (
    id bigint NOT NULL,
    "venueId" bigint,
    "providerId" bigint NOT NULL,
    "idAtProvider" text NOT NULL
);



--
-- Name: cinema_provider_pivot_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.cinema_provider_pivot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: cinema_provider_pivot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.cinema_provider_pivot_id_seq OWNED BY public.cinema_provider_pivot.id;


--
-- Name: collective_booking; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_booking (
    id bigint NOT NULL,
    "bookingId" bigint,
    "dateCreated" timestamp without time zone NOT NULL,
    "dateUsed" timestamp without time zone,
    "collectiveStockId" bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "offererId" bigint NOT NULL,
    "cancellationDate" timestamp without time zone,
    "cancellationLimitDate" timestamp without time zone NOT NULL,
    "cancellationReason" public.bookingcancellationreasons,
    status public.bookingstatus NOT NULL,
    "reimbursementDate" timestamp without time zone,
    "educationalInstitutionId" bigint NOT NULL,
    "educationalYearId" character varying(30) NOT NULL,
    "confirmationDate" timestamp without time zone,
    "confirmationLimitDate" timestamp without time zone NOT NULL,
    "educationalRedactorId" bigint NOT NULL
);



--
-- Name: collective_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.collective_booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: collective_booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.collective_booking_id_seq OWNED BY public.collective_booking.id;


--
-- Name: collective_offer; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_offer (
    "audioDisabilityCompliant" boolean,
    "mentalDisabilityCompliant" boolean,
    "motorDisabilityCompliant" boolean,
    "visualDisabilityCompliant" boolean,
    "lastValidationDate" timestamp without time zone,
    validation public.validation_status DEFAULT 'APPROVED'::public.validation_status NOT NULL,
    id bigint NOT NULL,
    "offerId" bigint,
    "isActive" boolean DEFAULT true NOT NULL,
    "venueId" bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    "durationMinutes" integer,
    "dateCreated" timestamp without time zone NOT NULL,
    "subcategoryId" text NOT NULL,
    "dateUpdated" timestamp without time zone,
    students public.studentlevels[] DEFAULT '{}'::public.studentlevels[] NOT NULL,
    "contactEmail" character varying(120) NOT NULL,
    "contactPhone" text NOT NULL,
    "offerVenue" jsonb NOT NULL,
    "lastValidationType" public.validation_type,
    "institutionId" bigint,
    "interventionArea" text[] DEFAULT '{}'::text[] NOT NULL,
    "bookingEmails" character varying[] DEFAULT '{}'::character varying[] NOT NULL,
    "templateId" bigint,
    "isPublicApi" boolean DEFAULT false NOT NULL,
    "imageCrop" jsonb,
    "imageCredit" text,
    "imageHasOriginal" boolean
);



--
-- Name: collective_offer_domain; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_offer_domain (
    "collectiveOfferId" bigint NOT NULL,
    "educationalDomainId" bigint NOT NULL
);



--
-- Name: collective_offer_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.collective_offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: collective_offer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.collective_offer_id_seq OWNED BY public.collective_offer.id;


--
-- Name: collective_offer_template; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_offer_template (
    "audioDisabilityCompliant" boolean,
    "mentalDisabilityCompliant" boolean,
    "motorDisabilityCompliant" boolean,
    "visualDisabilityCompliant" boolean,
    "lastValidationDate" timestamp without time zone,
    validation public.validation_status DEFAULT 'APPROVED'::public.validation_status NOT NULL,
    id bigint NOT NULL,
    "offerId" bigint,
    "isActive" boolean DEFAULT true NOT NULL,
    "venueId" bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text DEFAULT ''::text NOT NULL,
    "durationMinutes" integer,
    "dateCreated" timestamp without time zone NOT NULL,
    "subcategoryId" text NOT NULL,
    "dateUpdated" timestamp without time zone,
    students public.studentlevels[] DEFAULT '{}'::public.studentlevels[] NOT NULL,
    "priceDetail" text,
    "contactEmail" character varying(120) NOT NULL,
    "contactPhone" text NOT NULL,
    "offerVenue" jsonb NOT NULL,
    "lastValidationType" public.validation_type,
    "interventionArea" text[] DEFAULT '{}'::text[] NOT NULL,
    "bookingEmails" character varying[] DEFAULT '{}'::character varying[] NOT NULL,
    "imageCrop" jsonb,
    "imageCredit" text,
    "imageHasOriginal" boolean
);



--
-- Name: collective_offer_template_domain; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_offer_template_domain (
    "collectiveOfferTemplateId" bigint NOT NULL,
    "educationalDomainId" bigint NOT NULL
);



--
-- Name: collective_offer_template_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.collective_offer_template_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: collective_offer_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.collective_offer_template_id_seq OWNED BY public.collective_offer_template.id;


--
-- Name: collective_stock; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.collective_stock (
    id bigint NOT NULL,
    "stockId" bigint,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    "beginningDatetime" timestamp without time zone NOT NULL,
    "collectiveOfferId" bigint NOT NULL,
    price numeric(10,2) NOT NULL,
    "bookingLimitDatetime" timestamp without time zone NOT NULL,
    "numberOfTickets" integer NOT NULL,
    "priceDetail" text
);



--
-- Name: collective_stock_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.collective_stock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: collective_stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.collective_stock_id_seq OWNED BY public.collective_stock.id;


--
-- Name: criterion; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.criterion (
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    "endDateTime" timestamp without time zone,
    "startDateTime" timestamp without time zone
);



--
-- Name: criterion_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.criterion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: criterion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.criterion_id_seq OWNED BY public.criterion.id;


--
-- Name: custom_reimbursement_rule; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.custom_reimbursement_rule (
    id bigint NOT NULL,
    "offerId" bigint,
    amount numeric(10,2),
    timespan tsrange,
    rate numeric(5,4),
    categories text[] DEFAULT '{}'::text[],
    "offererId" bigint,
    subcategories text[] DEFAULT '{}'::text[],
    CONSTRAINT amount_or_rate_check CHECK ((num_nonnulls(amount, rate) = 1)),
    CONSTRAINT custom_reimbursement_rule_timespan_check CHECK ((lower(timespan) IS NOT NULL)),
    CONSTRAINT offer_or_offerer_check CHECK ((num_nonnulls("offerId", "offererId") = 1)),
    CONSTRAINT rate_range_check CHECK (((rate IS NULL) OR ((rate >= (0)::numeric) AND (rate <= (1)::numeric))))
);



--
-- Name: custom_reimbursement_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.custom_reimbursement_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: custom_reimbursement_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.custom_reimbursement_rule_id_seq OWNED BY public.custom_reimbursement_rule.id;


--
-- Name: deposit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.deposit (
    id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "userId" bigint NOT NULL,
    source character varying(300) NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    version smallint NOT NULL,
    "expirationDate" timestamp without time zone,
    type character varying DEFAULT 'GRANT_18'::character varying NOT NULL,
    "dateUpdated" timestamp without time zone
);



--
-- Name: deposit_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.deposit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: deposit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.deposit_id_seq OWNED BY public.deposit.id;


--
-- Name: educational_deposit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_deposit (
    id bigint NOT NULL,
    "educationalInstitutionId" bigint NOT NULL,
    "educationalYearId" character varying(30) NOT NULL,
    amount numeric(10,2) NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    "isFinal" boolean NOT NULL,
    ministry public.ministry
);



--
-- Name: educational_deposit_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_deposit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_deposit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_deposit_id_seq OWNED BY public.educational_deposit.id;


--
-- Name: educational_domain; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_domain (
    id bigint NOT NULL,
    name text NOT NULL
);



--
-- Name: educational_domain_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_domain_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_domain_id_seq OWNED BY public.educational_domain.id;


--
-- Name: educational_domain_venue; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_domain_venue (
    id bigint NOT NULL,
    "educationalDomainId" bigint NOT NULL,
    "venueId" bigint NOT NULL
);



--
-- Name: educational_domain_venue_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_domain_venue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_domain_venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_domain_venue_id_seq OWNED BY public.educational_domain_venue.id;


--
-- Name: educational_institution; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_institution (
    id integer NOT NULL,
    "institutionId" character varying(30) NOT NULL,
    city text NOT NULL,
    email text,
    name text NOT NULL,
    "phoneNumber" character varying(30) NOT NULL,
    "postalCode" character varying(10) NOT NULL,
    "institutionType" character varying(80) NOT NULL
);



--
-- Name: educational_institution_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_institution_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_institution_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_institution_id_seq OWNED BY public.educational_institution.id;


--
-- Name: educational_redactor; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_redactor (
    id bigint NOT NULL,
    email character varying(120) NOT NULL,
    "firstName" character varying(128),
    "lastName" character varying(128),
    civility character varying(20)
);



--
-- Name: educational_redactor_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_redactor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_redactor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_redactor_id_seq OWNED BY public.educational_redactor.id;


--
-- Name: educational_year; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.educational_year (
    id bigint NOT NULL,
    "beginningDate" timestamp without time zone NOT NULL,
    "expirationDate" timestamp without time zone NOT NULL,
    "adageId" character varying(30) NOT NULL
);



--
-- Name: educational_year_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.educational_year_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: educational_year_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.educational_year_id_seq OWNED BY public.educational_year.id;


--
-- Name: external_booking; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.external_booking (
    id bigint NOT NULL,
    "bookingId" bigint NOT NULL,
    barcode character varying NOT NULL,
    seat character varying
);



--
-- Name: external_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.external_booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: external_booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.external_booking_id_seq OWNED BY public.external_booking.id;


--
-- Name: favorite; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.favorite (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "offerId" bigint NOT NULL,
    "mediationId" bigint,
    "dateCreated" timestamp without time zone
);



--
-- Name: favorite_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.favorite_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: favorite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.favorite_id_seq OWNED BY public.favorite.id;


--
-- Name: feature; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.feature (
    id bigint NOT NULL,
    name text NOT NULL,
    description character varying(300) NOT NULL,
    "isActive" boolean DEFAULT true NOT NULL
);



--
-- Name: feature_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.feature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: feature_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.feature_id_seq OWNED BY public.feature.id;


--
-- Name: individual_booking; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.individual_booking (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "depositId" bigint
);



--
-- Name: individual_booking_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.individual_booking_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: individual_booking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.individual_booking_id_seq OWNED BY public.individual_booking.id;


--
-- Name: invoice; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.invoice (
    id bigint NOT NULL,
    date timestamp without time zone DEFAULT now() NOT NULL,
    reference text NOT NULL,
    "businessUnitId" bigint,
    amount integer NOT NULL,
    token text NOT NULL,
    "reimbursementPointId" bigint
);



--
-- Name: invoice_cashflow; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.invoice_cashflow (
    "invoiceId" bigint NOT NULL,
    "cashflowId" bigint NOT NULL
);



--
-- Name: invoice_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.invoice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: invoice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.invoice_id_seq OWNED BY public.invoice.id;


--
-- Name: invoice_line; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.invoice_line (
    id bigint NOT NULL,
    "invoiceId" bigint NOT NULL,
    label text NOT NULL,
    "group" jsonb NOT NULL,
    "contributionAmount" integer NOT NULL,
    "reimbursedAmount" integer NOT NULL,
    rate numeric(5,4) NOT NULL
);



--
-- Name: invoice_line_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.invoice_line_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: invoice_line_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.invoice_line_id_seq OWNED BY public.invoice_line.id;


--
-- Name: latest_dms_import; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.latest_dms_import (
    id bigint NOT NULL,
    "procedureId" integer NOT NULL,
    "latestImportDatetime" timestamp without time zone NOT NULL,
    "isProcessing" boolean NOT NULL,
    "processedApplications" integer[] NOT NULL
);



--
-- Name: latest_dms_import_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.latest_dms_import_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: latest_dms_import_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.latest_dms_import_id_seq OWNED BY public.latest_dms_import.id;


--
-- Name: local_provider_event; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.local_provider_event (
    id bigint NOT NULL,
    "providerId" bigint NOT NULL,
    date timestamp without time zone NOT NULL,
    type public.localprovidereventtype NOT NULL,
    payload character varying(50)
);



--
-- Name: local_provider_event_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.local_provider_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: local_provider_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.local_provider_event_id_seq OWNED BY public.local_provider_event.id;


--
-- Name: mediation; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.mediation (
    "thumbCount" integer NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "authorId" bigint,
    "lastProviderId" bigint,
    "offerId" bigint NOT NULL,
    credit character varying(255),
    "isActive" boolean DEFAULT true NOT NULL,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: mediation_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.mediation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: mediation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.mediation_id_seq OWNED BY public.mediation.id;


--
-- Name: offer; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offer (
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "productId" bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "lastProviderId" bigint,
    "bookingEmail" character varying(120),
    "isActive" boolean DEFAULT true NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    conditions character varying(120),
    "ageMin" integer,
    "ageMax" integer,
    url character varying(255),
    "mediaUrls" character varying(220)[] NOT NULL,
    "durationMinutes" integer,
    "isNational" boolean NOT NULL,
    "isDuo" boolean DEFAULT false NOT NULL,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "withdrawalDetails" text,
    "audioDisabilityCompliant" boolean,
    "mentalDisabilityCompliant" boolean,
    "motorDisabilityCompliant" boolean,
    "visualDisabilityCompliant" boolean,
    "externalTicketOfficeUrl" character varying,
    validation public.validation_status DEFAULT 'APPROVED'::public.validation_status NOT NULL,
    "rankingWeight" integer,
    "authorId" bigint,
    "idAtProvider" text,
    "lastValidationDate" timestamp without time zone,
    "subcategoryId" text NOT NULL,
    "dateUpdated" timestamp without time zone,
    "jsonData" jsonb,
    "lastValidationType" public.validation_type,
    "withdrawalDelay" bigint,
    "withdrawalType" character varying,
    CONSTRAINT check_providable_with_provider_has_idatprovider CHECK ((('lastProviderId' IS NULL) OR ('idAtProvider' IS NOT NULL)))
);



--
-- Name: offer_criterion; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offer_criterion (
    id bigint NOT NULL,
    "offerId" bigint NOT NULL,
    "criterionId" bigint NOT NULL
);



--
-- Name: offer_criterion_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offer_criterion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offer_criterion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offer_criterion_id_seq OWNED BY public.offer_criterion.id;


--
-- Name: offer_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offer_id_seq OWNED BY public.offer.id;


--
-- Name: offer_report; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offer_report (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "offerId" bigint NOT NULL,
    "reportedAt" timestamp without time zone DEFAULT now() NOT NULL,
    reason text NOT NULL,
    "customReasonContent" text,
    CONSTRAINT custom_reason_null_only_if_reason_is_other CHECK ((((reason <> 'OTHER'::text) AND ("customReasonContent" IS NULL)) OR ((reason = 'OTHER'::text) AND ("customReasonContent" IS NOT NULL) AND (btrim("customReasonContent", ' '::text) <> ''::text))))
);



--
-- Name: offer_report_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offer_report_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offer_report_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offer_report_id_seq OWNED BY public.offer_report.id;


--
-- Name: offer_validation_config; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offer_validation_config (
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "userId" bigint,
    specs jsonb NOT NULL
);



--
-- Name: offer_validation_config_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offer_validation_config_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offer_validation_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offer_validation_config_id_seq OWNED BY public.offer_validation_config.id;


--
-- Name: offerer; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offerer (
    "isActive" boolean DEFAULT true NOT NULL,
    "thumbCount" integer NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    address character varying(200),
    "postalCode" character varying(6) NOT NULL,
    city character varying(50) NOT NULL,
    "validationToken" character varying(27),
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    name character varying(140) NOT NULL,
    siren character varying(9),
    "lastProviderId" bigint,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "dateValidated" timestamp without time zone,
    "validationStatus" public.validationstatus,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: offerer_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offerer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offerer_id_seq OWNED BY public.offerer.id;


--
-- Name: offerer_tag; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offerer_tag (
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    label character varying(140),
    description text,
    "categoryId" text
);



--
-- Name: offerer_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offerer_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offerer_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offerer_tag_id_seq OWNED BY public.offerer_tag.id;


--
-- Name: offerer_tag_mapping; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.offerer_tag_mapping (
    id bigint NOT NULL,
    "offererId" bigint NOT NULL,
    "tagId" bigint NOT NULL
);



--
-- Name: offerer_tag_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.offerer_tag_mapping_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: offerer_tag_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.offerer_tag_mapping_id_seq OWNED BY public.offerer_tag_mapping.id;


--
-- Name: orphan_dms_application; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.orphan_dms_application (
    id bigint NOT NULL,
    email text,
    application_id bigint NOT NULL,
    process_id bigint,
    "dateCreated" timestamp without time zone,
    latest_modification_datetime timestamp without time zone
);



--
-- Name: orphan_dms_application_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.orphan_dms_application_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: orphan_dms_application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.orphan_dms_application_id_seq OWNED BY public.orphan_dms_application.id;


--
-- Name: payment; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.payment (
    id bigint NOT NULL,
    author character varying(27) NOT NULL,
    comment text,
    "recipientName" character varying(140) NOT NULL,
    iban character varying(27),
    bic character varying(11),
    "bookingId" bigint,
    amount numeric(10,2) NOT NULL,
    "reimbursementRule" character varying(200),
    "transactionEndToEndId" uuid,
    "recipientSiren" character varying(9) NOT NULL,
    "reimbursementRate" numeric(10,2),
    "transactionLabel" character varying(140),
    "paymentMessageId" bigint,
    "batchDate" timestamp without time zone,
    "customReimbursementRuleId" bigint,
    "collectiveBookingId" bigint,
    CONSTRAINT reimbursement_constraint_check CHECK (((("reimbursementRule" IS NOT NULL) AND ("reimbursementRate" IS NOT NULL) AND ("customReimbursementRuleId" IS NULL)) OR (("reimbursementRule" IS NULL) AND ("customReimbursementRuleId" IS NOT NULL))))
);



--
-- Name: payment_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.payment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.payment_id_seq OWNED BY public.payment.id;


--
-- Name: payment_message; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.payment_message (
    id bigint NOT NULL,
    name character varying(50) NOT NULL,
    checksum bytea NOT NULL
);



--
-- Name: payment_message_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.payment_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: payment_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.payment_message_id_seq OWNED BY public.payment_message.id;


--
-- Name: payment_status; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.payment_status (
    id bigint NOT NULL,
    "paymentId" bigint NOT NULL,
    date timestamp without time zone DEFAULT now() NOT NULL,
    status public.transactionstatus NOT NULL,
    detail character varying
);



--
-- Name: payment_status_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.payment_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: payment_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.payment_status_id_seq OWNED BY public.payment_status.id;


--
-- Name: permission; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.permission (
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    category character varying(140)
);



--
-- Name: permission_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.permission_id_seq OWNED BY public.permission.id;


--
-- Name: pricing; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.pricing (
    id bigint NOT NULL,
    status text NOT NULL,
    "bookingId" bigint,
    "businessUnitId" bigint,
    "creationDate" timestamp without time zone DEFAULT now() NOT NULL,
    "valueDate" timestamp without time zone NOT NULL,
    amount integer NOT NULL,
    "standardRule" text NOT NULL,
    "customRuleId" bigint,
    revenue integer NOT NULL,
    siret character varying(14),
    "collectiveBookingId" bigint,
    "pricingPointId" bigint,
    "venueId" bigint,
    CONSTRAINT booking_xor_collective_booking_check CHECK ((num_nonnulls("bookingId", "collectiveBookingId") = 1)),
    CONSTRAINT reimbursement_rule_constraint_check CHECK (((("standardRule" = ''::text) AND ("customRuleId" IS NOT NULL)) OR (("standardRule" <> ''::text) AND ("customRuleId" IS NULL))))
);



--
-- Name: pricing_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.pricing_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: pricing_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.pricing_id_seq OWNED BY public.pricing.id;


--
-- Name: pricing_line; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.pricing_line (
    id bigint NOT NULL,
    "pricingId" bigint,
    amount integer NOT NULL,
    category text NOT NULL
);



--
-- Name: pricing_line_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.pricing_line_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: pricing_line_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.pricing_line_id_seq OWNED BY public.pricing_line.id;


--
-- Name: pricing_log; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.pricing_log (
    id bigint NOT NULL,
    "pricingId" bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    "statusBefore" text NOT NULL,
    "statusAfter" text NOT NULL,
    reason text NOT NULL
);



--
-- Name: pricing_log_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.pricing_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: pricing_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.pricing_log_id_seq OWNED BY public.pricing_log.id;


--
-- Name: product; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.product (
    "thumbCount" integer NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    conditions character varying(120),
    "ageMin" integer,
    "ageMax" integer,
    "mediaUrls" character varying(220)[] NOT NULL,
    "durationMinutes" integer,
    "isNational" boolean DEFAULT false NOT NULL,
    "lastProviderId" bigint,
    "owningOffererId" integer,
    url character varying(255),
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "isGcuCompatible" boolean DEFAULT true NOT NULL,
    "subcategoryId" text NOT NULL,
    "isSynchronizationCompatible" boolean DEFAULT true NOT NULL,
    "jsonData" jsonb,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- Name: provider; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.provider (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    name character varying(90) NOT NULL,
    "localClass" character varying(60),
    "enabledForPro" boolean DEFAULT false NOT NULL,
    "apiUrl" character varying,
    "authToken" character varying,
    "pricesInCents" boolean DEFAULT false NOT NULL,
    "enableParallelSynchronization" boolean DEFAULT false NOT NULL,
    CONSTRAINT "check_provider_has_localclass_or_apiUrl" CHECK (((("localClass" IS NOT NULL) AND ("apiUrl" IS NULL)) OR (("localClass" IS NULL) AND ("apiUrl" IS NOT NULL))))
);



--
-- Name: provider_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.provider_id_seq OWNED BY public.provider.id;


--
-- Name: recredit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.recredit (
    id bigint NOT NULL,
    "depositId" bigint NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    amount numeric(10,2) NOT NULL,
    "recreditType" text NOT NULL,
    comment text
);



--
-- Name: recredit_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.recredit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: recredit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.recredit_id_seq OWNED BY public.recredit.id;


--
-- Name: reference_scheme; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.reference_scheme (
    id bigint NOT NULL,
    name text NOT NULL,
    prefix text NOT NULL,
    year integer,
    "nextNumber" integer,
    "numberPadding" integer
);



--
-- Name: reference_scheme_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.reference_scheme_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: reference_scheme_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.reference_scheme_id_seq OWNED BY public.reference_scheme.id;


--
-- Name: role; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.role (
    id bigint NOT NULL,
    name character varying(140) NOT NULL
);



--
-- Name: role_backoffice_profile; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.role_backoffice_profile (
    "roleId" bigint NOT NULL,
    "profileId" bigint NOT NULL
);



--
-- Name: role_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.role_id_seq OWNED BY public.role.id;


--
-- Name: role_permission_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.role_permission_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: role_permission; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.role_permission (
    "roleId" bigint,
    "permissionId" bigint,
    id bigint DEFAULT nextval('public.role_permission_seq'::regclass) NOT NULL
);



--
-- Name: stock; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.stock (
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateModified" timestamp without time zone NOT NULL,
    price numeric(10,2) NOT NULL,
    quantity integer,
    "bookingLimitDatetime" timestamp without time zone,
    "lastProviderId" bigint,
    "offerId" bigint NOT NULL,
    "isSoftDeleted" boolean DEFAULT false NOT NULL,
    "beginningDatetime" timestamp without time zone,
    "dateCreated" timestamp without time zone DEFAULT now() NOT NULL,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "dnBookedQuantity" bigint DEFAULT 0 NOT NULL,
    "rawProviderQuantity" integer,
    "numberOfTickets" integer,
    "educationalPriceDetail" text,
    CONSTRAINT check_price_is_not_negative CHECK ((price >= (0)::numeric)),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: stock_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.stock_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.stock_id_seq OWNED BY public.stock.id;


--
-- Name: token; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.token (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    value character varying NOT NULL,
    type character varying NOT NULL,
    "creationDate" timestamp without time zone DEFAULT now() NOT NULL,
    "expirationDate" timestamp without time zone,
    "isUsed" boolean DEFAULT false NOT NULL,
    "extraData" jsonb
);



--
-- Name: token_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.token_id_seq OWNED BY public.token.id;


--
-- Name: transaction; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.transaction (
    id bigint NOT NULL,
    native_transaction_id bigint,
    issued_at timestamp without time zone,
    client_addr inet,
    actor_id bigint
);



--
-- Name: transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.transaction_id_seq OWNED BY public.transaction.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public."user" (
    id bigint NOT NULL,
    "validationToken" character varying(27),
    email character varying(120) NOT NULL,
    password bytea NOT NULL,
    "publicName" character varying(255) NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "departementCode" character varying(3),
    "firstName" character varying(128),
    "lastName" character varying(128),
    "postalCode" character varying(5),
    "phoneNumber" character varying(20),
    "dateOfBirth" timestamp without time zone,
    "needsToFillCulturalSurvey" boolean DEFAULT true,
    "culturalSurveyId" uuid,
    civility character varying(20),
    activity character varying(128),
    "culturalSurveyFilledDate" timestamp without time zone,
    address text,
    city character varying(100),
    "lastConnectionDate" timestamp without time zone,
    "isEmailValidated" boolean DEFAULT false,
    "isActive" boolean DEFAULT true NOT NULL,
    "hasSeenProTutorials" boolean DEFAULT false NOT NULL,
    "notificationSubscriptions" jsonb DEFAULT '{"marketing_push": true, "marketing_email": true}'::jsonb,
    "phoneValidationStatus" character varying,
    "hasCompletedIdCheck" boolean,
    "idPieceNumber" character varying,
    "externalIds" jsonb DEFAULT '{}'::jsonb,
    roles character varying[] DEFAULT '{}'::character varying[] NOT NULL,
    "extraData" jsonb DEFAULT '{}'::jsonb,
    "ineHash" text,
    "recreditAmountToShow" numeric(10,2),
    "schoolType" text,
    comment text,
    married_name character varying(128),
    "hasSeenProRgs" boolean DEFAULT false NOT NULL,
    "validatedBirthDate" date,
    CONSTRAINT check_admin_is_never_beneficiary CHECK ((NOT ((('BENEFICIARY'::text = ANY ((roles)::text[])) OR ('UNDERAGE_BENEFICIARY'::text = ANY ((roles)::text[]))) AND ('ADMIN'::text = ANY ((roles)::text[])))))
);



--
-- Name: user_email_history; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.user_email_history (
    id bigint NOT NULL,
    "userId" bigint,
    "oldUserEmail" character varying(120) NOT NULL,
    "oldDomainEmail" character varying(120) NOT NULL,
    "newUserEmail" character varying(120) NOT NULL,
    "newDomainEmail" character varying(120) NOT NULL,
    "creationDate" timestamp without time zone DEFAULT now() NOT NULL,
    "eventType" character varying NOT NULL
);



--
-- Name: user_email_history_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.user_email_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_email_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.user_email_history_id_seq OWNED BY public.user_email_history.id;


--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: user_offerer; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.user_offerer (
    id bigint NOT NULL,
    "validationToken" character varying(27),
    "userId" bigint NOT NULL,
    "offererId" bigint NOT NULL,
    "validationStatus" public.validationstatus
);



--
-- Name: user_offerer_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.user_offerer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_offerer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.user_offerer_id_seq OWNED BY public.user_offerer.id;


--
-- Name: user_session; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.user_session (
    id bigint NOT NULL,
    uuid uuid NOT NULL,
    "userId" bigint NOT NULL
);



--
-- Name: user_session_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.user_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.user_session_id_seq OWNED BY public.user_session.id;


--
-- Name: user_suspension; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.user_suspension (
    id bigint NOT NULL,
    "userId" bigint NOT NULL,
    "eventType" character varying NOT NULL,
    "eventDate" timestamp without time zone DEFAULT now(),
    "actorUserId" bigint,
    "reasonCode" character varying
);



--
-- Name: user_suspension_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.user_suspension_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: user_suspension_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.user_suspension_id_seq OWNED BY public.user_suspension.id;


--
-- Name: venue; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue (
    "thumbCount" integer NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    address character varying(200),
    "postalCode" character varying(6),
    city character varying(50),
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    siret character varying(14),
    "departementCode" character varying(3),
    latitude numeric(8,5),
    longitude numeric(8,5),
    "managingOffererId" bigint NOT NULL,
    "bookingEmail" character varying(120),
    "lastProviderId" bigint,
    "isVirtual" boolean DEFAULT false NOT NULL,
    comment text,
    "publicName" character varying(255),
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "venueTypeId" integer,
    "venueLabelId" integer,
    "dateCreated" timestamp without time zone NOT NULL,
    "isPermanent" boolean,
    "withdrawalDetails" text,
    "venueTypeCode" character varying,
    description text,
    "audioDisabilityCompliant" boolean,
    "mentalDisabilityCompliant" boolean,
    "motorDisabilityCompliant" boolean,
    "visualDisabilityCompliant" boolean,
    "bannerMeta" jsonb,
    "bannerUrl" text,
    "businessUnitId" integer,
    "adageId" text,
    "dmsToken" text,
    "venueEducationalStatusId" bigint,
    "collectiveDescription" text,
    "collectiveStudents" public.studentlevels[] DEFAULT '{}'::public.studentlevels[],
    "collectiveWebsite" text,
    "collectiveInterventionArea" jsonb,
    "collectiveNetwork" jsonb,
    "collectiveAccessInformation" text,
    "collectivePhone" text,
    "collectiveEmail" text,
    CONSTRAINT "check_has_siret_xor_comment_xor_isVirtual" CHECK ((((siret IS NULL) AND (comment IS NULL) AND ("isVirtual" IS TRUE)) OR ((siret IS NULL) AND (comment IS NOT NULL) AND ("isVirtual" IS FALSE)) OR ((siret IS NOT NULL) AND ("isVirtual" IS FALSE)))),
    CONSTRAINT check_is_virtual_xor_has_address CHECK (((("isVirtual" IS TRUE) AND ((address IS NULL) AND ("postalCode" IS NULL) AND (city IS NULL) AND ("departementCode" IS NULL))) OR (("isVirtual" IS FALSE) AND (siret IS NOT NULL) AND (("postalCode" IS NOT NULL) AND (city IS NOT NULL) AND ("departementCode" IS NOT NULL))) OR (("isVirtual" IS FALSE) AND ((siret IS NULL) AND (comment IS NOT NULL)) AND ((address IS NOT NULL) AND ("postalCode" IS NOT NULL) AND (city IS NOT NULL) AND ("departementCode" IS NOT NULL))))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: venue_contact; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_contact (
    id bigint NOT NULL,
    "venueId" bigint NOT NULL,
    email character varying(256),
    website character varying(256),
    phone_number character varying(64),
    social_medias jsonb DEFAULT '{}'::jsonb NOT NULL
);



--
-- Name: venue_contact_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_contact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_contact_id_seq OWNED BY public.venue_contact.id;


--
-- Name: venue_criterion; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_criterion (
    id bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "criterionId" bigint NOT NULL
);



--
-- Name: venue_criterion_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_criterion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_criterion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_criterion_id_seq OWNED BY public.venue_criterion.id;


--
-- Name: venue_educational_status; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_educational_status (
    id bigint NOT NULL,
    name character varying(256) NOT NULL
);



--
-- Name: venue_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_id_seq OWNED BY public.venue.id;


--
-- Name: venue_label; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_label (
    id integer NOT NULL,
    label character varying(100) NOT NULL
);



--
-- Name: venue_label_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_label_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_label_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_label_id_seq OWNED BY public.venue_label.id;


--
-- Name: venue_pricing_point_link; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_pricing_point_link (
    id bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "pricingPointId" bigint NOT NULL,
    timespan tsrange NOT NULL
);



--
-- Name: venue_pricing_point_link_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_pricing_point_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_pricing_point_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_pricing_point_link_id_seq OWNED BY public.venue_pricing_point_link.id;


--
-- Name: venue_provider; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_provider (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    "venueId" bigint NOT NULL,
    "providerId" bigint NOT NULL,
    "venueIdAtOfferProvider" character varying(70) NOT NULL,
    "lastSyncDate" timestamp without time zone,
    "lastProviderId" bigint,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "isDuoOffers" boolean,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
);



--
-- Name: venue_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_provider_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_provider_id_seq OWNED BY public.venue_provider.id;


--
-- Name: venue_reimbursement_point_link; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_reimbursement_point_link (
    id bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "reimbursementPointId" bigint NOT NULL,
    timespan tsrange NOT NULL
);



--
-- Name: venue_reimbursement_point_link_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_reimbursement_point_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_reimbursement_point_link_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_reimbursement_point_link_id_seq OWNED BY public.venue_reimbursement_point_link.id;


--
-- Name: venue_type; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_type (
    id integer NOT NULL,
    label character varying(100) NOT NULL
);



--
-- Name: venue_type_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.venue_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: venue_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.venue_type_id_seq OWNED BY public.venue_type.id;


--
-- Name: action_history id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history ALTER COLUMN id SET DEFAULT nextval('public.action_history_id_seq'::regclass);


--
-- Name: activation_code id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activation_code ALTER COLUMN id SET DEFAULT nextval('public.activation_code_id_seq'::regclass);


--
-- Name: activity id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activity ALTER COLUMN id SET DEFAULT nextval('public.activity_id_seq'::regclass);


--
-- Name: allocine_pivot id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot ALTER COLUMN id SET DEFAULT nextval('public.allocine_pivot_id_seq'::regclass);


--
-- Name: allocine_theater id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_theater ALTER COLUMN id SET DEFAULT nextval('public.allocine_theater_id_seq'::regclass);


--
-- Name: allocine_venue_provider_price_rule id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider_price_rule ALTER COLUMN id SET DEFAULT nextval('public.allocine_venue_provider_price_rule_id_seq'::regclass);


--
-- Name: api_key id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.api_key ALTER COLUMN id SET DEFAULT nextval('public.api_key_id_seq'::regclass);


--
-- Name: backoffice_user_profile id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.backoffice_user_profile ALTER COLUMN id SET DEFAULT nextval('public.backoffice_user_profile_id_seq'::regclass);


--
-- Name: bank_information id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information ALTER COLUMN id SET DEFAULT nextval('public.bank_information_id_seq'::regclass);


--
-- Name: beneficiary_fraud_check id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_check ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_fraud_check_id_seq'::regclass);


--
-- Name: beneficiary_fraud_review id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_review ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_fraud_review_id_seq'::regclass);


--
-- Name: beneficiary_import id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_import_id_seq'::regclass);


--
-- Name: beneficiary_import_status id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import_status ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_import_status_id_seq'::regclass);


--
-- Name: book_macro_section id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.book_macro_section ALTER COLUMN id SET DEFAULT nextval('public.book_macro_section_id_seq'::regclass);


--
-- Name: booking id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq'::regclass);


--
-- Name: boost_cinema_details id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.boost_cinema_details ALTER COLUMN id SET DEFAULT nextval('public.boost_cinema_details_id_seq'::regclass);


--
-- Name: business_unit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit ALTER COLUMN id SET DEFAULT nextval('public.business_unit_id_seq'::regclass);


--
-- Name: business_unit_venue_link id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit_venue_link ALTER COLUMN id SET DEFAULT nextval('public.business_unit_venue_link_id_seq'::regclass);


--
-- Name: cashflow id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow ALTER COLUMN id SET DEFAULT nextval('public.cashflow_id_seq'::regclass);


--
-- Name: cashflow_batch id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_batch ALTER COLUMN id SET DEFAULT nextval('public.cashflow_batch_id_seq'::regclass);


--
-- Name: cashflow_log id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_log ALTER COLUMN id SET DEFAULT nextval('public.cashflow_log_id_seq'::regclass);


--
-- Name: cds_cinema_details id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cds_cinema_details ALTER COLUMN id SET DEFAULT nextval('public.cds_cinema_details_id_seq'::regclass);


--
-- Name: cinema_provider_pivot id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot ALTER COLUMN id SET DEFAULT nextval('public.cinema_provider_pivot_id_seq'::regclass);


--
-- Name: collective_booking id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking ALTER COLUMN id SET DEFAULT nextval('public.collective_booking_id_seq'::regclass);


--
-- Name: collective_offer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer ALTER COLUMN id SET DEFAULT nextval('public.collective_offer_id_seq'::regclass);


--
-- Name: collective_offer_template id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template ALTER COLUMN id SET DEFAULT nextval('public.collective_offer_template_id_seq'::regclass);


--
-- Name: collective_stock id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_stock ALTER COLUMN id SET DEFAULT nextval('public.collective_stock_id_seq'::regclass);


--
-- Name: criterion id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.criterion ALTER COLUMN id SET DEFAULT nextval('public.criterion_id_seq'::regclass);


--
-- Name: custom_reimbursement_rule id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.custom_reimbursement_rule ALTER COLUMN id SET DEFAULT nextval('public.custom_reimbursement_rule_id_seq'::regclass);


--
-- Name: deposit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit ALTER COLUMN id SET DEFAULT nextval('public.deposit_id_seq'::regclass);


--
-- Name: educational_deposit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_deposit ALTER COLUMN id SET DEFAULT nextval('public.educational_deposit_id_seq'::regclass);


--
-- Name: educational_domain id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain ALTER COLUMN id SET DEFAULT nextval('public.educational_domain_id_seq'::regclass);


--
-- Name: educational_domain_venue id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain_venue ALTER COLUMN id SET DEFAULT nextval('public.educational_domain_venue_id_seq'::regclass);


--
-- Name: educational_institution id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_institution ALTER COLUMN id SET DEFAULT nextval('public.educational_institution_id_seq'::regclass);


--
-- Name: educational_redactor id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_redactor ALTER COLUMN id SET DEFAULT nextval('public.educational_redactor_id_seq'::regclass);


--
-- Name: educational_year id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_year ALTER COLUMN id SET DEFAULT nextval('public.educational_year_id_seq'::regclass);


--
-- Name: external_booking id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.external_booking ALTER COLUMN id SET DEFAULT nextval('public.external_booking_id_seq'::regclass);


--
-- Name: favorite id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite ALTER COLUMN id SET DEFAULT nextval('public.favorite_id_seq'::regclass);


--
-- Name: feature id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.feature ALTER COLUMN id SET DEFAULT nextval('public.feature_id_seq'::regclass);


--
-- Name: individual_booking id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.individual_booking ALTER COLUMN id SET DEFAULT nextval('public.individual_booking_id_seq'::regclass);


--
-- Name: invoice id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice ALTER COLUMN id SET DEFAULT nextval('public.invoice_id_seq'::regclass);


--
-- Name: invoice_line id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_line ALTER COLUMN id SET DEFAULT nextval('public.invoice_line_id_seq'::regclass);


--
-- Name: latest_dms_import id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.latest_dms_import ALTER COLUMN id SET DEFAULT nextval('public.latest_dms_import_id_seq'::regclass);


--
-- Name: local_provider_event id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.local_provider_event ALTER COLUMN id SET DEFAULT nextval('public.local_provider_event_id_seq'::regclass);


--
-- Name: mediation id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation ALTER COLUMN id SET DEFAULT nextval('public.mediation_id_seq'::regclass);


--
-- Name: offer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer ALTER COLUMN id SET DEFAULT nextval('public.offer_id_seq'::regclass);


--
-- Name: offer_criterion id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion ALTER COLUMN id SET DEFAULT nextval('public.offer_criterion_id_seq'::regclass);


--
-- Name: offer_report id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_report ALTER COLUMN id SET DEFAULT nextval('public.offer_report_id_seq'::regclass);


--
-- Name: offer_validation_config id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_validation_config ALTER COLUMN id SET DEFAULT nextval('public.offer_validation_config_id_seq'::regclass);


--
-- Name: offerer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer ALTER COLUMN id SET DEFAULT nextval('public.offerer_id_seq'::regclass);


--
-- Name: offerer_tag id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag ALTER COLUMN id SET DEFAULT nextval('public.offerer_tag_id_seq'::regclass);


--
-- Name: offerer_tag_mapping id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag_mapping ALTER COLUMN id SET DEFAULT nextval('public.offerer_tag_mapping_id_seq'::regclass);


--
-- Name: orphan_dms_application id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.orphan_dms_application ALTER COLUMN id SET DEFAULT nextval('public.orphan_dms_application_id_seq'::regclass);


--
-- Name: payment id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment ALTER COLUMN id SET DEFAULT nextval('public.payment_id_seq'::regclass);


--
-- Name: payment_message id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_message ALTER COLUMN id SET DEFAULT nextval('public.payment_message_id_seq'::regclass);


--
-- Name: payment_status id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_status ALTER COLUMN id SET DEFAULT nextval('public.payment_status_id_seq'::regclass);


--
-- Name: permission id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.permission ALTER COLUMN id SET DEFAULT nextval('public.permission_id_seq'::regclass);


--
-- Name: pricing id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing ALTER COLUMN id SET DEFAULT nextval('public.pricing_id_seq'::regclass);


--
-- Name: pricing_line id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_line ALTER COLUMN id SET DEFAULT nextval('public.pricing_line_id_seq'::regclass);


--
-- Name: pricing_log id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_log ALTER COLUMN id SET DEFAULT nextval('public.pricing_log_id_seq'::regclass);


--
-- Name: product id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: provider id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.provider ALTER COLUMN id SET DEFAULT nextval('public.provider_id_seq'::regclass);


--
-- Name: recredit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.recredit ALTER COLUMN id SET DEFAULT nextval('public.recredit_id_seq'::regclass);


--
-- Name: reference_scheme id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.reference_scheme ALTER COLUMN id SET DEFAULT nextval('public.reference_scheme_id_seq'::regclass);


--
-- Name: role id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.role_id_seq'::regclass);


--
-- Name: stock id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.stock ALTER COLUMN id SET DEFAULT nextval('public.stock_id_seq'::regclass);


--
-- Name: token id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.token ALTER COLUMN id SET DEFAULT nextval('public.token_id_seq'::regclass);


--
-- Name: transaction id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.transaction ALTER COLUMN id SET DEFAULT nextval('public.transaction_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: user_email_history id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_email_history ALTER COLUMN id SET DEFAULT nextval('public.user_email_history_id_seq'::regclass);


--
-- Name: user_offerer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer ALTER COLUMN id SET DEFAULT nextval('public.user_offerer_id_seq'::regclass);


--
-- Name: user_session id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_session ALTER COLUMN id SET DEFAULT nextval('public.user_session_id_seq'::regclass);


--
-- Name: user_suspension id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_suspension ALTER COLUMN id SET DEFAULT nextval('public.user_suspension_id_seq'::regclass);


--
-- Name: venue id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue ALTER COLUMN id SET DEFAULT nextval('public.venue_id_seq'::regclass);


--
-- Name: venue_contact id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_contact ALTER COLUMN id SET DEFAULT nextval('public.venue_contact_id_seq'::regclass);


--
-- Name: venue_criterion id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_criterion ALTER COLUMN id SET DEFAULT nextval('public.venue_criterion_id_seq'::regclass);


--
-- Name: venue_label id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_label ALTER COLUMN id SET DEFAULT nextval('public.venue_label_id_seq'::regclass);


--
-- Name: venue_pricing_point_link id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_pricing_point_link ALTER COLUMN id SET DEFAULT nextval('public.venue_pricing_point_link_id_seq'::regclass);


--
-- Name: venue_provider id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider ALTER COLUMN id SET DEFAULT nextval('public.venue_provider_id_seq'::regclass);


--
-- Name: venue_reimbursement_point_link id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_reimbursement_point_link ALTER COLUMN id SET DEFAULT nextval('public.venue_reimbursement_point_link_id_seq'::regclass);


--
-- Name: venue_type id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_type ALTER COLUMN id SET DEFAULT nextval('public.venue_type_id_seq'::regclass);


--
-- Data for Name: action_history; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: activation_code; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: activity; Type: TABLE DATA; Schema: public; Owner: pass_culture
--





--
-- Data for Name: allocine_pivot; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: allocine_theater; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: allocine_venue_provider; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: allocine_venue_provider_price_rule; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: api_key; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: backoffice_user_profile; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: bank_information; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: beneficiary_fraud_check; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: beneficiary_fraud_review; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: beneficiary_import; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: beneficiary_import_status; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: book_macro_section; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.book_macro_section VALUES (1, 'Jeunesse', 'documentaire jeunesse nature');
INSERT INTO public.book_macro_section VALUES (2, 'Jeunesse', 'documentaire jeunesse');
INSERT INTO public.book_macro_section VALUES (3, 'Jeunesse', 'documentaire jeunesse audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (4, 'Jeunesse', 'documentaire jeunesse géographie atlas');
INSERT INTO public.book_macro_section VALUES (5, 'Jeunesse', 'documentaire jeunesse histoire');
INSERT INTO public.book_macro_section VALUES (6, 'Jeunesse', 'documentaire jeunesse encyclopédies et dictionnaires');
INSERT INTO public.book_macro_section VALUES (7, 'Jeunesse', 'documentaire jeunesse art et culture');
INSERT INTO public.book_macro_section VALUES (8, 'Jeunesse', 'documentaire jeunesse religion');
INSERT INTO public.book_macro_section VALUES (9, 'Jeunesse', 'documentaire jeunesse sciences');
INSERT INTO public.book_macro_section VALUES (10, 'Jeunesse', 'documentaire jeunesse revues');
INSERT INTO public.book_macro_section VALUES (11, 'Jeunesse', 'documentaires et activités d''éveil pour la jeunesse');
INSERT INTO public.book_macro_section VALUES (12, 'Jeunesse', 'littérature jeunesse romans / contes / fables poche');
INSERT INTO public.book_macro_section VALUES (13, 'Jeunesse', 'littérature jeunesse romans / contes / fables');
INSERT INTO public.book_macro_section VALUES (14, 'Jeunesse', 'jeunesse');
INSERT INTO public.book_macro_section VALUES (15, 'Jeunesse', 'activité jeunesse 1er âge tva 5.5');
INSERT INTO public.book_macro_section VALUES (16, 'Jeunesse', 'littérature jeunesse albums');
INSERT INTO public.book_macro_section VALUES (17, 'Jeunesse', 'littérature jeunesse');
INSERT INTO public.book_macro_section VALUES (18, 'Jeunesse', 'littérature jeunesse audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (19, 'Jeunesse', 'jeunesse en langue anglaise');
INSERT INTO public.book_macro_section VALUES (20, 'Jeunesse', 'littérature jeunesse revues');
INSERT INTO public.book_macro_section VALUES (21, 'Jeunesse', 'jeunesse en langue allemande');
INSERT INTO public.book_macro_section VALUES (22, 'Bandes dessinées', 'bandes dessinées adultes / comics');
INSERT INTO public.book_macro_section VALUES (23, 'Bandes dessinées', 'bandes dessinées jeunesse');
INSERT INTO public.book_macro_section VALUES (24, 'Bandes dessinées', 'bandes dessinées');
INSERT INTO public.book_macro_section VALUES (25, 'Bandes dessinées', 'bandes dessinées audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (26, 'Bandes dessinées', 'bandes dessinées revues');
INSERT INTO public.book_macro_section VALUES (27, 'Bandes dessinées', 'bd et humour en langue anglaise');
INSERT INTO public.book_macro_section VALUES (28, 'Bandes dessinées', 'bd et humour en langue allemande');
INSERT INTO public.book_macro_section VALUES (29, 'Littérature française', 'littérature romans poche');
INSERT INTO public.book_macro_section VALUES (30, 'Littérature française', 'poche revues');
INSERT INTO public.book_macro_section VALUES (31, 'Littérature française', 'littérature française romans nouvelles correspondance');
INSERT INTO public.book_macro_section VALUES (32, 'Littérature française', 'littérature française romans historiques');
INSERT INTO public.book_macro_section VALUES (33, 'Littérature française', 'littérature française récits, aventures, voyages');
INSERT INTO public.book_macro_section VALUES (34, 'Littérature française', 'littérature française');
INSERT INTO public.book_macro_section VALUES (35, 'Littérature française', 'littérature française audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (36, 'Littérature française', 'littérature française romans régionaux');
INSERT INTO public.book_macro_section VALUES (37, 'Littérature française', 'littérature française revues');
INSERT INTO public.book_macro_section VALUES (38, 'Littérature française', 'romans au format poche');
INSERT INTO public.book_macro_section VALUES (39, 'Littérature française', 'autobiographies contemporaines anthologies/dico');
INSERT INTO public.book_macro_section VALUES (40, 'Littérature française', 'contes et légendes');
INSERT INTO public.book_macro_section VALUES (41, 'Littérature française', 'petits prix');
INSERT INTO public.book_macro_section VALUES (42, 'Littérature Etrangère', 'littérature étrangère');
INSERT INTO public.book_macro_section VALUES (43, 'Littérature Etrangère', 'littérature étrangère audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (44, 'Littérature Etrangère', 'littérature asie (hors japon)');
INSERT INTO public.book_macro_section VALUES (45, 'Littérature Etrangère', 'littérature moyen orient');
INSERT INTO public.book_macro_section VALUES (46, 'Littérature Etrangère', 'littérature étrangère romans historiques');
INSERT INTO public.book_macro_section VALUES (47, 'Littérature Etrangère', 'littérature japon');
INSERT INTO public.book_macro_section VALUES (48, 'Littérature Etrangère', 'littérature afrique du nord');
INSERT INTO public.book_macro_section VALUES (49, 'Littérature Etrangère', 'littérature en langue étrangère');
INSERT INTO public.book_macro_section VALUES (50, 'Littérature Etrangère', 'littérature afrique noire');
INSERT INTO public.book_macro_section VALUES (51, 'Littérature Etrangère', 'littérature étrangère revues');
INSERT INTO public.book_macro_section VALUES (52, 'Littérature Etrangère', 'littérature afrique subsaharienne');
INSERT INTO public.book_macro_section VALUES (53, ' Droit', 'poche droit');
INSERT INTO public.book_macro_section VALUES (54, ' Droit', 'droit');
INSERT INTO public.book_macro_section VALUES (55, ' Droit', 'droit audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (56, ' Droit', 'droit essais');
INSERT INTO public.book_macro_section VALUES (57, ' Droit', 'droit public, droit administratif');
INSERT INTO public.book_macro_section VALUES (58, ' Droit', 'droit constitutionnel');
INSERT INTO public.book_macro_section VALUES (59, ' Droit', 'droit fiscal');
INSERT INTO public.book_macro_section VALUES (60, ' Droit', 'relations et droit international');
INSERT INTO public.book_macro_section VALUES (61, ' Droit', 'droit civil et procédure civile');
INSERT INTO public.book_macro_section VALUES (62, ' Droit', 'droit pénal et procédure pénale');
INSERT INTO public.book_macro_section VALUES (63, ' Droit', 'droit commercial et des sociétés');
INSERT INTO public.book_macro_section VALUES (64, ' Droit', 'droit du travail et social');
INSERT INTO public.book_macro_section VALUES (65, ' Droit', 'droit pratique et correspondance');
INSERT INTO public.book_macro_section VALUES (66, ' Droit', 'histoire du droit et institutions publiques');
INSERT INTO public.book_macro_section VALUES (67, ' Droit', 'autres droits privés');
INSERT INTO public.book_macro_section VALUES (68, ' Droit', 'droit revues');
INSERT INTO public.book_macro_section VALUES (69, ' Droit', 'droit de l''urbanisme et environnement');
INSERT INTO public.book_macro_section VALUES (70, ' Droit', 'droit contrats types ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (71, 'Art', 'peinture / dessin d''art / gravure');
INSERT INTO public.book_macro_section VALUES (72, 'Art', 'art en langue anglaise');
INSERT INTO public.book_macro_section VALUES (73, 'Art', 'art et civilisation');
INSERT INTO public.book_macro_section VALUES (74, 'Art', 'art religieux');
INSERT INTO public.book_macro_section VALUES (75, 'Art', 'art en langue allemande');
INSERT INTO public.book_macro_section VALUES (76, 'Art', 'sculpture');
INSERT INTO public.book_macro_section VALUES (77, 'Poèsie, théâtre et spectacle', 'poésie grand format');
INSERT INTO public.book_macro_section VALUES (78, 'Poèsie, théâtre et spectacle', 'poésie format poche');
INSERT INTO public.book_macro_section VALUES (79, 'Poèsie, théâtre et spectacle', 'arts et spectacle audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (80, 'Poèsie, théâtre et spectacle', 'arts et spectacles');
INSERT INTO public.book_macro_section VALUES (81, 'Poèsie, théâtre et spectacle', 'théâtre');
INSERT INTO public.book_macro_section VALUES (82, 'Poèsie, théâtre et spectacle', 'poésie théâtre revues');
INSERT INTO public.book_macro_section VALUES (83, 'Poèsie, théâtre et spectacle', 'arts et spectacle revues');
INSERT INTO public.book_macro_section VALUES (84, 'Poèsie, théâtre et spectacle', 'poésie & théâtre');
INSERT INTO public.book_macro_section VALUES (85, 'Poèsie, théâtre et spectacle', 'poésie théâtre audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (86, ' Arts Culinaires', 'produits pour la cuisine');
INSERT INTO public.book_macro_section VALUES (87, ' Arts Culinaires', 'arts de la table : recettes');
INSERT INTO public.book_macro_section VALUES (88, ' Arts Culinaires', 'cuisines étrangères');
INSERT INTO public.book_macro_section VALUES (89, ' Arts Culinaires', 'arts de la table');
INSERT INTO public.book_macro_section VALUES (90, ' Arts Culinaires', 'arts de la table audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (91, ' Arts Culinaires', 'gastronomie et décoration de la table');
INSERT INTO public.book_macro_section VALUES (92, ' Arts Culinaires', 'arts de la table revues');
INSERT INTO public.book_macro_section VALUES (93, ' Tourisme', 'tourisme europe (hors france) guides');
INSERT INTO public.book_macro_section VALUES (94, ' Tourisme', 'tourisme france guides');
INSERT INTO public.book_macro_section VALUES (95, ' Tourisme', 'tourisme afrique guides');
INSERT INTO public.book_macro_section VALUES (96, ' Tourisme', 'tourisme asie / moyen-orient guides');
INSERT INTO public.book_macro_section VALUES (97, ' Tourisme', 'tourisme france livres');
INSERT INTO public.book_macro_section VALUES (98, ' Tourisme', 'tourisme océanie / pacifique guides');
INSERT INTO public.book_macro_section VALUES (99, ' Tourisme', 'tourisme amérique du nord / du sud guides');
INSERT INTO public.book_macro_section VALUES (100, ' Tourisme', 'tourisme & voyages livres');
INSERT INTO public.book_macro_section VALUES (101, 'Tourisme', 'tourisme europe (hors france) livres');
INSERT INTO public.book_macro_section VALUES (102, 'Tourisme', 'tourisme & voyage guides');
INSERT INTO public.book_macro_section VALUES (103, 'Tourisme', 'tourisme france cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (104, 'Tourisme', 'tourisme & voyages');
INSERT INTO public.book_macro_section VALUES (105, 'Tourisme', 'voyages / tourisme / géographie en langue anglaise');
INSERT INTO public.book_macro_section VALUES (106, 'Tourisme', 'tourisme cartes spécialisées');
INSERT INTO public.book_macro_section VALUES (107, 'Tourisme', 'tourisme asie / moyen-orient livres');
INSERT INTO public.book_macro_section VALUES (108, 'Tourisme', 'tourisme & voyages (cartes, plans, atlas routiers,...)');
INSERT INTO public.book_macro_section VALUES (109, 'Tourisme', 'tourisme afrique livres');
INSERT INTO public.book_macro_section VALUES (110, 'Tourisme', 'tourisme amérique du nord / du sud cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (111, 'Tourisme', 'tourisme océanie / pacifique livres');
INSERT INTO public.book_macro_section VALUES (112, 'Tourisme', 'tourisme amérique du nord / du sud livres');
INSERT INTO public.book_macro_section VALUES (113, 'Tourisme', 'voyages / tourisme / géographie en langue allemande');
INSERT INTO public.book_macro_section VALUES (114, 'Tourisme', 'tourisme europe (hors france) cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (115, 'Tourisme', 'tourisme revues');
INSERT INTO public.book_macro_section VALUES (116, 'Tourisme', 'tourisme asie / moyen-orient cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (117, 'Tourisme', 'tourisme audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (118, 'Tourisme', 'tourisme afrique cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (119, 'Tourisme', 'tourisme cartes marines');
INSERT INTO public.book_macro_section VALUES (120, 'Tourisme', 'tourisme océanie / pacifique cartes, plans, atlas routiers');
INSERT INTO public.book_macro_section VALUES (121, 'Littérature Europééne', 'littérature italienne');
INSERT INTO public.book_macro_section VALUES (122, 'Littérature Europééne', 'littérature anglo-saxonne');
INSERT INTO public.book_macro_section VALUES (123, 'Littérature Europééne', 'littérature hispano-portugaise');
INSERT INTO public.book_macro_section VALUES (124, 'Littérature Europééne', 'littérature allemande');
INSERT INTO public.book_macro_section VALUES (125, 'Littérature Europééne', 'littérature nordique');
INSERT INTO public.book_macro_section VALUES (126, 'Littérature Europééne', 'littératures européennes rares');
INSERT INTO public.book_macro_section VALUES (127, 'Littérature Europééne', 'anglais ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (128, 'Littérature Europééne', 'espagnol ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (129, 'Littérature Europééne', 'italien ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (130, 'Littérature Europééne', 'allemand ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (131, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique poche');
INSERT INTO public.book_macro_section VALUES (132, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique');
INSERT INTO public.book_macro_section VALUES (133, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (134, 'Sciences Humaines, Encyclopédie, dictionnaire', 'textes et commentaires petits classiques');
INSERT INTO public.book_macro_section VALUES (135, 'Sciences Humaines, Encyclopédie, dictionnaire', 'poche philosophie');
INSERT INTO public.book_macro_section VALUES (136, 'Sciences Humaines, Encyclopédie, dictionnaire', 'philosophie');
INSERT INTO public.book_macro_section VALUES (137, 'Sciences Humaines, Encyclopédie, dictionnaire', 'philosophie audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (138, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique critiques et essais');
INSERT INTO public.book_macro_section VALUES (139, 'Sciences Humaines, Encyclopédie, dictionnaire', 'monographie / histoire de l''art / essais / dictionnaires');
INSERT INTO public.book_macro_section VALUES (140, 'Sciences Humaines, Encyclopédie, dictionnaire', 'philosophie dictionnaires et ouvrages généraux');
INSERT INTO public.book_macro_section VALUES (141, 'Sciences Humaines, Encyclopédie, dictionnaire', 'philosophie textes / critiques / essais / commentaires');
INSERT INTO public.book_macro_section VALUES (142, 'Sciences Humaines, Encyclopédie, dictionnaire', 'dictionnaires de langue française');
INSERT INTO public.book_macro_section VALUES (143, 'Sciences Humaines, Encyclopédie, dictionnaire', 'dictionnaires de langue française audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (144, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique dictionnaires et méthodes');
INSERT INTO public.book_macro_section VALUES (145, 'Sciences Humaines, Encyclopédie, dictionnaire', 'textes et commentaires');
INSERT INTO public.book_macro_section VALUES (146, 'Sciences Humaines, Encyclopédie, dictionnaire', 'médecine histoire, dictionnaires et essais');
INSERT INTO public.book_macro_section VALUES (147, 'Sciences Humaines, Encyclopédie, dictionnaire', 'nature encyclopédie');
INSERT INTO public.book_macro_section VALUES (148, 'Sciences Humaines, Encyclopédie, dictionnaire', 'dictionnaires et atlas historiques');
INSERT INTO public.book_macro_section VALUES (149, 'Sciences Humaines, Encyclopédie, dictionnaire', 'géographie atlas et dictionnaires');
INSERT INTO public.book_macro_section VALUES (150, 'Sciences Humaines, Encyclopédie, dictionnaire', 'sociologie dictionnaires et lexiques');
INSERT INTO public.book_macro_section VALUES (151, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique textes');
INSERT INTO public.book_macro_section VALUES (152, 'Sciences Humaines, Encyclopédie, dictionnaire', 'encyclopédies animales');
INSERT INTO public.book_macro_section VALUES (153, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique revues');
INSERT INTO public.book_macro_section VALUES (154, 'Sciences Humaines, Encyclopédie, dictionnaire', 'philosophie revues');
INSERT INTO public.book_macro_section VALUES (155, 'Sciences Humaines, Encyclopédie, dictionnaire', 'lettres et linguistique latin grec');
INSERT INTO public.book_macro_section VALUES (156, 'Sciences Humaines, Encyclopédie, dictionnaire', 'santé et dictionnaires');
INSERT INTO public.book_macro_section VALUES (157, 'Sciences Humaines, Encyclopédie, dictionnaire', 'encyclopédies et autres religions');
INSERT INTO public.book_macro_section VALUES (158, 'Sciences Humaines, Encyclopédie, dictionnaire', 'textes et commentaires autres');
INSERT INTO public.book_macro_section VALUES (159, 'Sciences Humaines, Encyclopédie, dictionnaire', 'textes et commentaires littéraires et philosophiques');
INSERT INTO public.book_macro_section VALUES (160, 'Sciences Humaines, Encyclopédie, dictionnaire', 'sports encyclopédies, pédagogie, encyclopédies généralistes');
INSERT INTO public.book_macro_section VALUES (161, 'Sciences Humaines, Encyclopédie, dictionnaire', 'dictionnaires spécialisés de langue française / divers');
INSERT INTO public.book_macro_section VALUES (162, 'Sciences Humaines, Encyclopédie, dictionnaire', 'encyclopédies');
INSERT INTO public.book_macro_section VALUES (163, 'Sciences Humaines, Encyclopédie, dictionnaire', 'dictionnaires de langue française revues');
INSERT INTO public.book_macro_section VALUES (164, 'Sciences Humaines, Encyclopédie, dictionnaire', 'epistémologie');
INSERT INTO public.book_macro_section VALUES (165, 'Sexualité', 'littérature sentimentale poche');
INSERT INTO public.book_macro_section VALUES (166, 'Sexualité', 'littérature érotique');
INSERT INTO public.book_macro_section VALUES (167, 'Sexualité', 'sexualité');
INSERT INTO public.book_macro_section VALUES (168, 'Sexualité', 'orientation');
INSERT INTO public.book_macro_section VALUES (169, 'Sexualité', 'poche érotique');
INSERT INTO public.book_macro_section VALUES (170, 'Informatique', 'informatique - internet');
INSERT INTO public.book_macro_section VALUES (171, 'Informatique', 'informatique livres matériel et application mac');
INSERT INTO public.book_macro_section VALUES (172, 'Informatique', 'informatique langages et programmation');
INSERT INTO public.book_macro_section VALUES (173, 'Informatique', 'informatique bureautique');
INSERT INTO public.book_macro_section VALUES (174, 'Informatique', 'informatique réseaux et internet');
INSERT INTO public.book_macro_section VALUES (175, 'Informatique', 'informatique livres matériel p.c. et multimédia');
INSERT INTO public.book_macro_section VALUES (176, 'Informatique', 'informatique systèmes d''exploitation');
INSERT INTO public.book_macro_section VALUES (177, 'Informatique', 'informatique revues');
INSERT INTO public.book_macro_section VALUES (178, 'Informatique', 'informatique audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (179, 'Informatique', 'informatique revues anglo saxonnes');
INSERT INTO public.book_macro_section VALUES (180, 'Informatique', 'informatique / internet en langue anglaise');
INSERT INTO public.book_macro_section VALUES (181, 'Informatique', 'informatique livres anglo saxon');
INSERT INTO public.book_macro_section VALUES (182, 'Histoire', 'biographies historiques');
INSERT INTO public.book_macro_section VALUES (183, 'Histoire', 'histoire de l''europe');
INSERT INTO public.book_macro_section VALUES (184, 'Histoire', 'histoire');
INSERT INTO public.book_macro_section VALUES (185, 'Histoire', 'poche histoire');
INSERT INTO public.book_macro_section VALUES (186, 'Histoire', 'histoire audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (187, 'Histoire', 'histoire essais');
INSERT INTO public.book_macro_section VALUES (188, 'Histoire', 'histoire du moyen age au 19ème siècle');
INSERT INTO public.book_macro_section VALUES (189, 'Histoire', 'histoire du 20ème siècle à nos jours');
INSERT INTO public.book_macro_section VALUES (190, 'Histoire', 'histoire revues');
INSERT INTO public.book_macro_section VALUES (191, 'Histoire', 'histoire / actualité en langue anglaise');
INSERT INTO public.book_macro_section VALUES (192, 'Histoire', 'histoire / actualité en langue allemande');
INSERT INTO public.book_macro_section VALUES (193, 'Histoire', 'mythologie préhistoire antiquité et autres civilisations');
INSERT INTO public.book_macro_section VALUES (194, 'Histoire', 'généalogie héraldique');
INSERT INTO public.book_macro_section VALUES (195, 'Sciences, vie & Nature', 'médecine (ouvrages de référence)');
INSERT INTO public.book_macro_section VALUES (196, 'Sciences, vie & Nature', 'faune revues');
INSERT INTO public.book_macro_section VALUES (197, 'Sciences, vie & Nature', 'sciences appliquées mathématiques');
INSERT INTO public.book_macro_section VALUES (198, 'Sciences, vie & Nature', 'médecine revues');
INSERT INTO public.book_macro_section VALUES (199, 'Sciences, vie & Nature', 'paramédical revues');
INSERT INTO public.book_macro_section VALUES (200, 'Sciences, vie & Nature', 'santé revues');
INSERT INTO public.book_macro_section VALUES (201, 'Sciences, vie & Nature', 'sciences de la vie et de la terre, botanique, ecologie');
INSERT INTO public.book_macro_section VALUES (202, 'Sciences, vie & Nature', 'sciences politiques essais');
INSERT INTO public.book_macro_section VALUES (203, 'Sciences, vie & Nature', 'poche médecine');
INSERT INTO public.book_macro_section VALUES (204, 'Sciences, vie & Nature', 'médecine audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (205, 'Sciences, vie & Nature', 'sciences appliquées astronomie, astrophysique');
INSERT INTO public.book_macro_section VALUES (206, 'Sciences, vie & Nature', 'politique géopolitique');
INSERT INTO public.book_macro_section VALUES (207, 'Sciences, vie & Nature', 'sciences politiques');
INSERT INTO public.book_macro_section VALUES (208, 'Sciences, vie & Nature', 'sciences humaines (economie, psychologie, politique, droit, philosophie, art,..)');
INSERT INTO public.book_macro_section VALUES (209, 'Sciences, vie & Nature', 'poches sciences appliquées');
INSERT INTO public.book_macro_section VALUES (210, 'Sciences, vie & Nature', 'sciences appliquées bâtiments et travaux publics');
INSERT INTO public.book_macro_section VALUES (211, 'Sciences, vie & Nature', 'médecines naturelles et parallèles');
INSERT INTO public.book_macro_section VALUES (212, 'Sciences, vie & Nature', 'sciences appliquées');
INSERT INTO public.book_macro_section VALUES (213, 'Sciences, vie & Nature', 'sciences appliquées audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (214, 'Sciences, vie & Nature', 'sciences appliquées physique');
INSERT INTO public.book_macro_section VALUES (215, 'Sciences, vie & Nature', 'sciences appliquées electronique');
INSERT INTO public.book_macro_section VALUES (216, 'Sciences, vie & Nature', 'sciences appliquées chimie');
INSERT INTO public.book_macro_section VALUES (217, 'Sciences, vie & Nature', 'sciences appliquées agro-alimentaire, agronomie, agriculture');
INSERT INTO public.book_macro_section VALUES (218, 'Sciences, vie & Nature', 'sciences appliquées revues');
INSERT INTO public.book_macro_section VALUES (219, 'Sciences, vie & Nature', 'médecine science fondamentale');
INSERT INTO public.book_macro_section VALUES (220, 'Sciences, vie & Nature', 'pharmacologie');
INSERT INTO public.book_macro_section VALUES (221, 'Sciences, vie & Nature', 'sciences politiques revues');
INSERT INTO public.book_macro_section VALUES (222, 'Sciences, vie & Nature', 'sciences / médecine en langue anglaise');
INSERT INTO public.book_macro_section VALUES (223, 'Sciences, vie & Nature', 'manuels de sciences politiques');
INSERT INTO public.book_macro_section VALUES (224, 'Sciences, vie & Nature', 'sciences humaines en langue anglaise');
INSERT INTO public.book_macro_section VALUES (225, 'Sciences, vie & Nature', 'internat et médecine interne');
INSERT INTO public.book_macro_section VALUES (226, 'Sciences, vie & Nature', 'sciences appliquées à la médecine');
INSERT INTO public.book_macro_section VALUES (227, 'Sciences, vie & Nature', 'sciences humaines en langue allemande');
INSERT INTO public.book_macro_section VALUES (228, 'Sciences, vie & Nature', 'sciences / médecine en langue allemande');
INSERT INTO public.book_macro_section VALUES (229, 'Sciences, vie & Nature', 'animaux domestiques et de compagnie');
INSERT INTO public.book_macro_section VALUES (230, 'Sciences, vie & Nature', 'nature');
INSERT INTO public.book_macro_section VALUES (231, 'Sciences, vie & Nature', 'nature audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (232, 'Sciences, vie & Nature', 'jardinage');
INSERT INTO public.book_macro_section VALUES (233, 'Sciences, vie & Nature', 'faune');
INSERT INTO public.book_macro_section VALUES (234, 'Sciences, vie & Nature', 'faune audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (235, 'Sciences, vie & Nature', 'oiseaux');
INSERT INTO public.book_macro_section VALUES (236, 'Sciences, vie & Nature', 'reptiles / batraciens / insectes');
INSERT INTO public.book_macro_section VALUES (237, 'Sciences, vie & Nature', 'petits élevages');
INSERT INTO public.book_macro_section VALUES (238, 'Sciences, vie & Nature', 'animaux sauvages');
INSERT INTO public.book_macro_section VALUES (239, 'Sciences, vie & Nature', 'roches, minéraux et fossiles');
INSERT INTO public.book_macro_section VALUES (240, 'Sciences, vie & Nature', 'aquariophilie et faune aquatique');
INSERT INTO public.book_macro_section VALUES (241, 'Sciences, vie & Nature', 'champignons');
INSERT INTO public.book_macro_section VALUES (242, 'Sciences, vie & Nature', 'nature revues');
INSERT INTO public.book_macro_section VALUES (243, 'Langue ', 'français langue étrangère lectures');
INSERT INTO public.book_macro_section VALUES (244, 'Langue ', 'langues étrangères');
INSERT INTO public.book_macro_section VALUES (245, 'Langue ', 'français langue étrangère');
INSERT INTO public.book_macro_section VALUES (246, 'Langue ', 'allemand revues');
INSERT INTO public.book_macro_section VALUES (247, 'Langue ', 'espagnol revues');
INSERT INTO public.book_macro_section VALUES (248, 'Langue ', 'italien revues');
INSERT INTO public.book_macro_section VALUES (249, 'Langue ', 'français langue étrangère audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (250, 'Langue ', 'français langue étrangère apprentissage');
INSERT INTO public.book_macro_section VALUES (251, 'Langue ', 'autres langues méthodes livres');
INSERT INTO public.book_macro_section VALUES (252, 'Langue ', 'autres langues ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (253, 'Langue ', 'langues rares (hors anglais, allemand, espagnol, italien, russe)');
INSERT INTO public.book_macro_section VALUES (254, 'Langue ', 'autres langues revues');
INSERT INTO public.book_macro_section VALUES (255, 'Langue ', 'anglais  revues');
INSERT INTO public.book_macro_section VALUES (256, 'Langue ', 'anglais enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (257, 'Langue ', 'espagnol enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (258, 'Langue ', 'allemand dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (259, 'Langue ', 'italien dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (260, 'Langue ', 'russe dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (261, 'Langue ', 'espagnol dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (262, 'Langue ', 'dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (263, 'Langue ', 'autres langues dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (264, 'Langue ', 'anglais (sans précision)');
INSERT INTO public.book_macro_section VALUES (265, 'Langue ', 'italien (sans précision)');
INSERT INTO public.book_macro_section VALUES (266, 'Langue ', 'anglais  audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (267, 'Langue ', 'méthodes langues');
INSERT INTO public.book_macro_section VALUES (268, 'Langue ', 'espagnol (sans précision)');
INSERT INTO public.book_macro_section VALUES (269, 'Langue ', 'autres langues enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (270, 'Langue ', 'français langue étrangère revues');
INSERT INTO public.book_macro_section VALUES (271, 'Langue ', 'allemand enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (272, 'Langue ', 'revues en langue étrangère');
INSERT INTO public.book_macro_section VALUES (273, 'Langue ', 'autres langues audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (274, 'Langue ', 'italien enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (275, 'Langue ', 'italien audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (276, 'Langue ', 'espagnol audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (277, 'Langue ', 'russe enseignement supérieur');
INSERT INTO public.book_macro_section VALUES (278, 'Langue ', 'economie en langue anglaise');
INSERT INTO public.book_macro_section VALUES (279, 'Langue ', 'allemand (sans précision)');
INSERT INTO public.book_macro_section VALUES (280, 'Langue ', 'allemand audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (281, 'Langue ', 'anglais dictionnaires et guides de conversation');
INSERT INTO public.book_macro_section VALUES (282, 'Langue ', 'scolaire en langue anglaise');
INSERT INTO public.book_macro_section VALUES (283, 'Langue ', 'enseignement supérieur de langues étrangères');
INSERT INTO public.book_macro_section VALUES (284, 'Langue ', 'universitaire, ouvrages de références, essais, livres en langue étrangère');
INSERT INTO public.book_macro_section VALUES (285, 'Langue ', 'non attribué / foires aux livres');
INSERT INTO public.book_macro_section VALUES (286, 'Langue ', 'anglais méthodes livres');
INSERT INTO public.book_macro_section VALUES (287, 'Langue ', 'papeterie ou merchandising');
INSERT INTO public.book_macro_section VALUES (288, 'Langue ', 'russe méthodes livres');
INSERT INTO public.book_macro_section VALUES (289, 'Langue ', 'littérature russe');
INSERT INTO public.book_macro_section VALUES (290, 'Langue ', 'espagnol méthodes livres');
INSERT INTO public.book_macro_section VALUES (291, 'Langue ', 'allemand méthodes livres');
INSERT INTO public.book_macro_section VALUES (292, 'Langue ', 'littérature collections de luxe');
INSERT INTO public.book_macro_section VALUES (293, 'Langue ', 'italien méthodes livres');
INSERT INTO public.book_macro_section VALUES (294, 'Langue ', 'qualité / production / logistique');
INSERT INTO public.book_macro_section VALUES (295, 'Langue ', 'supports hors livres & revues (k7,cd,...)en langue étrangère');
INSERT INTO public.book_macro_section VALUES (296, 'Langue ', 'rapports et planification française');
INSERT INTO public.book_macro_section VALUES (297, 'Langue ', 'russe ouvrages de littérature');
INSERT INTO public.book_macro_section VALUES (298, 'Langue ', 'russe revues');
INSERT INTO public.book_macro_section VALUES (299, 'Langue ', 'russe (sans précision)');
INSERT INTO public.book_macro_section VALUES (300, 'Langue ', 'russe audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (301, 'Economie', 'economie');
INSERT INTO public.book_macro_section VALUES (302, 'Economie', 'poche economie');
INSERT INTO public.book_macro_section VALUES (303, 'Economie', 'economie audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (304, 'Economie', 'comptabilité et finance');
INSERT INTO public.book_macro_section VALUES (305, 'Economie', 'essais d''economie générale');
INSERT INTO public.book_macro_section VALUES (306, 'Economie', 'théories et histoire économique');
INSERT INTO public.book_macro_section VALUES (307, 'Economie', 'comptabilité générale et plans comptables');
INSERT INTO public.book_macro_section VALUES (308, 'Economie', 'economie internationale');
INSERT INTO public.book_macro_section VALUES (309, 'Economie', 'entreprise revues');
INSERT INTO public.book_macro_section VALUES (310, 'Economie', 'expertise comptable');
INSERT INTO public.book_macro_section VALUES (311, 'Economie', 'gestion financière et fiscalité, bourse');
INSERT INTO public.book_macro_section VALUES (312, 'Economie', 'mathématiques économiques et financières');
INSERT INTO public.book_macro_section VALUES (313, 'Economie', 'economie française');
INSERT INTO public.book_macro_section VALUES (314, 'Economie', 'finances publiques');
INSERT INTO public.book_macro_section VALUES (315, 'Economie', 'economie revues');
INSERT INTO public.book_macro_section VALUES (316, 'Economie', 'comptabilité analytique');
INSERT INTO public.book_macro_section VALUES (317, 'Economie', 'comptabilité revues');
INSERT INTO public.book_macro_section VALUES (318, 'Economie', 'comptabilité audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (319, 'Scolaire & Parascolaire', 'manuels maternelles');
INSERT INTO public.book_macro_section VALUES (320, 'Scolaire & Parascolaire', 'poche universitaire revuesenseignement universitaire revues');
INSERT INTO public.book_macro_section VALUES (321, 'Scolaire & Parascolaire', 'pédagogie pour l''éducation');
INSERT INTO public.book_macro_section VALUES (322, 'Scolaire & Parascolaire', 'poche encyclopédique non universitaire');
INSERT INTO public.book_macro_section VALUES (323, 'Scolaire & Parascolaire', 'scolaire');
INSERT INTO public.book_macro_section VALUES (324, 'Scolaire & Parascolaire', 'pédagogie');
INSERT INTO public.book_macro_section VALUES (325, 'Scolaire & Parascolaire', 'pédagogie audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (326, 'Scolaire & Parascolaire', 'manuels maternelle et primaire');
INSERT INTO public.book_macro_section VALUES (327, 'Scolaire & Parascolaire', 'sciences appliquées autres technologies');
INSERT INTO public.book_macro_section VALUES (328, 'Scolaire & Parascolaire', 'enseignement universitaire');
INSERT INTO public.book_macro_section VALUES (329, 'Scolaire & Parascolaire', 'enseignement universitaire audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (330, 'Scolaire & Parascolaire', 'autres enseignements techniques lycées professionnels');
INSERT INTO public.book_macro_section VALUES (331, 'Scolaire & Parascolaire', 'manuels primaire audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (332, 'Scolaire & Parascolaire', 'manuels d''enseignement technique');
INSERT INTO public.book_macro_section VALUES (333, 'Scolaire & Parascolaire', 'enseignement universitaire annales');
INSERT INTO public.book_macro_section VALUES (334, 'Scolaire & Parascolaire', 'manuels lecture primaire');
INSERT INTO public.book_macro_section VALUES (335, 'Scolaire & Parascolaire', 'techniques du mieux être');
INSERT INTO public.book_macro_section VALUES (336, 'Scolaire & Parascolaire', 'manuels collège langues');
INSERT INTO public.book_macro_section VALUES (337, 'Scolaire & Parascolaire', 'manuels langues primaire');
INSERT INTO public.book_macro_section VALUES (338, 'Scolaire & Parascolaire', 'manuels d''enseignement tertiaire');
INSERT INTO public.book_macro_section VALUES (339, 'Scolaire & Parascolaire', 'entraînement et soutien lycée');
INSERT INTO public.book_macro_section VALUES (340, 'Scolaire & Parascolaire', 'manuels lycées français philosophie');
INSERT INTO public.book_macro_section VALUES (341, 'Scolaire & Parascolaire', 'enseignement tertiaire cap bep');
INSERT INTO public.book_macro_section VALUES (342, 'Scolaire & Parascolaire', 'poche universitaire encyclopédiques');
INSERT INTO public.book_macro_section VALUES (343, 'Scolaire & Parascolaire', 'poche universitaire pluridisciplinaires');
INSERT INTO public.book_macro_section VALUES (344, 'Scolaire & Parascolaire', 'manuels collège français');
INSERT INTO public.book_macro_section VALUES (345, 'Scolaire & Parascolaire', 'manuels mathématiques primaire');
INSERT INTO public.book_macro_section VALUES (346, 'Scolaire & Parascolaire', 'entraînement et soutien lycées techniques');
INSERT INTO public.book_macro_section VALUES (347, 'Scolaire & Parascolaire', 'enseignement général cap bep');
INSERT INTO public.book_macro_section VALUES (348, 'Scolaire & Parascolaire', 'entraînement et soutien collège');
INSERT INTO public.book_macro_section VALUES (349, 'Scolaire & Parascolaire', 'manuels autres matières primaire');
INSERT INTO public.book_macro_section VALUES (350, 'Scolaire & Parascolaire', 'annales collège');
INSERT INTO public.book_macro_section VALUES (351, 'Scolaire & Parascolaire', 'annales lycées techniques');
INSERT INTO public.book_macro_section VALUES (352, 'Scolaire & Parascolaire', 'manuels lycées d''enseignement général');
INSERT INTO public.book_macro_section VALUES (353, 'Scolaire & Parascolaire', 'manuels français primaire');
INSERT INTO public.book_macro_section VALUES (354, 'Scolaire & Parascolaire', 'annales lycée');
INSERT INTO public.book_macro_section VALUES (355, 'Scolaire & Parascolaire', 'manuels histoire / géographie / instruction civique primaire');
INSERT INTO public.book_macro_section VALUES (356, 'Scolaire & Parascolaire', 'manuels lycées langues vivantes');
INSERT INTO public.book_macro_section VALUES (357, 'Scolaire & Parascolaire', 'manuels collège');
INSERT INTO public.book_macro_section VALUES (358, 'Scolaire & Parascolaire', 'manuels collège audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (359, 'Scolaire & Parascolaire', 'autres enseignements techniques cap bep');
INSERT INTO public.book_macro_section VALUES (360, 'Scolaire & Parascolaire', 'enseignement général lycées professionnels');
INSERT INTO public.book_macro_section VALUES (361, 'Scolaire & Parascolaire', 'annales lycées professionnels');
INSERT INTO public.book_macro_section VALUES (362, 'Scolaire & Parascolaire', 'manuels collège mathématiques');
INSERT INTO public.book_macro_section VALUES (363, 'Scolaire & Parascolaire', 'manuels lycées audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (364, 'Scolaire & Parascolaire', 'manuels lycées mathématiques');
INSERT INTO public.book_macro_section VALUES (365, 'Scolaire & Parascolaire', 'enseignement tertiaire lycées professionnels');
INSERT INTO public.book_macro_section VALUES (366, 'Scolaire & Parascolaire', 'manuels lycées sciences économiques');
INSERT INTO public.book_macro_section VALUES (367, 'Scolaire & Parascolaire', 'manuels collège histoire / géographie / instruction civique');
INSERT INTO public.book_macro_section VALUES (368, 'Scolaire & Parascolaire', 'manuels collège latin grec');
INSERT INTO public.book_macro_section VALUES (369, 'Scolaire & Parascolaire', 'manuels lycées latin grec');
INSERT INTO public.book_macro_section VALUES (370, 'Scolaire & Parascolaire', 'manuels sciences et technologies primaire');
INSERT INTO public.book_macro_section VALUES (371, 'Scolaire & Parascolaire', 'manuels lycées autres matières');
INSERT INTO public.book_macro_section VALUES (372, 'Scolaire & Parascolaire', 'entraînement et soutien lycées professionnels');
INSERT INTO public.book_macro_section VALUES (373, 'Scolaire & Parascolaire', 'manuels collège autres matières');
INSERT INTO public.book_macro_section VALUES (374, 'Scolaire & Parascolaire', 'manuels lycées sciences physiques et chimie');
INSERT INTO public.book_macro_section VALUES (375, 'Scolaire & Parascolaire', 'poche universitaire tertiaire');
INSERT INTO public.book_macro_section VALUES (376, 'Scolaire & Parascolaire', 'autres enseignements techniques lycées techniques');
INSERT INTO public.book_macro_section VALUES (377, 'Scolaire & Parascolaire', 'enseignement technique audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (378, 'Scolaire & Parascolaire', 'manuels collège sciences de la vie et de la terre');
INSERT INTO public.book_macro_section VALUES (379, 'Scolaire & Parascolaire', 'sciences appliquées & livres techniques');
INSERT INTO public.book_macro_section VALUES (380, 'Scolaire & Parascolaire', 'logiciel educatif');
INSERT INTO public.book_macro_section VALUES (381, 'Scolaire & Parascolaire', 'manuels');
INSERT INTO public.book_macro_section VALUES (382, 'Scolaire & Parascolaire', 'manuels lycées histoire / géographie');
INSERT INTO public.book_macro_section VALUES (383, 'Scolaire & Parascolaire', 'annales cap bep');
INSERT INTO public.book_macro_section VALUES (384, 'Scolaire & Parascolaire', 'manuels lycées sciences de la vie et de la terre');
INSERT INTO public.book_macro_section VALUES (385, 'Scolaire & Parascolaire', 'pédagogie matériel tva 20');
INSERT INTO public.book_macro_section VALUES (386, 'Scolaire & Parascolaire', 'enseignement général lycées techniques');
INSERT INTO public.book_macro_section VALUES (387, 'Scolaire & Parascolaire', 'poche universitaire audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (388, 'Scolaire & Parascolaire', 'poche universitaire');
INSERT INTO public.book_macro_section VALUES (389, 'Scolaire & Parascolaire', 'entraînement et soutien cap bep');
INSERT INTO public.book_macro_section VALUES (390, 'Scolaire & Parascolaire', 'manuels d''enseignement industriel');
INSERT INTO public.book_macro_section VALUES (391, 'Scolaire & Parascolaire', 'manuels collège sciences physiques');
INSERT INTO public.book_macro_section VALUES (392, 'Scolaire & Parascolaire', 'enseignement industriel cap bep');
INSERT INTO public.book_macro_section VALUES (393, 'Scolaire & Parascolaire', 'enseignement industriel lycées professionnels');
INSERT INTO public.book_macro_section VALUES (394, 'Scolaire & Parascolaire', 'enseignement tertiaire lycées techniques');
INSERT INTO public.book_macro_section VALUES (395, 'Scolaire & Parascolaire', 'soutien et entraînement');
INSERT INTO public.book_macro_section VALUES (396, 'Scolaire & Parascolaire', 'enseignement industriel lycées techniques');
INSERT INTO public.book_macro_section VALUES (397, 'Scolaire & Parascolaire', 'parascolaire technique');
INSERT INTO public.book_macro_section VALUES (398, 'Scolaire & Parascolaire', 'esotérisme matériel tva 20');
INSERT INTO public.book_macro_section VALUES (399, 'Scolaire & Parascolaire', 'enseignement technique revues');
INSERT INTO public.book_macro_section VALUES (400, 'Scolaire & Parascolaire', 'manuels lycées revues');
INSERT INTO public.book_macro_section VALUES (401, 'Scolaire & Parascolaire', 'enseignement');
INSERT INTO public.book_macro_section VALUES (402, 'Scolaire & Parascolaire', 'poche universitaire industriel');
INSERT INTO public.book_macro_section VALUES (403, 'Scolaire & Parascolaire', 'cahiers de vacances primaire');
INSERT INTO public.book_macro_section VALUES (404, 'Scolaire & Parascolaire', 'cahiers de vacances maternelle');
INSERT INTO public.book_macro_section VALUES (405, 'Scolaire & Parascolaire', 'cahier soutien primaire');
INSERT INTO public.book_macro_section VALUES (406, 'Scolaire & Parascolaire', 'cahiers de vacances collège lycée');
INSERT INTO public.book_macro_section VALUES (407, 'Scolaire & Parascolaire', 'parascolaire secondaire');
INSERT INTO public.book_macro_section VALUES (408, 'Scolaire & Parascolaire', 'cahiers de vacances');
INSERT INTO public.book_macro_section VALUES (409, 'Scolaire & Parascolaire', 'parascolaire primaire audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (410, 'Scolaire & Parascolaire', 'parascolaire primaire');
INSERT INTO public.book_macro_section VALUES (411, 'Scolaire & Parascolaire', 'parascolaire secondaire revues');
INSERT INTO public.book_macro_section VALUES (412, 'Scolaire & Parascolaire', 'parascolaire');
INSERT INTO public.book_macro_section VALUES (413, 'Scolaire & Parascolaire', 'parascolaire maternelle audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (414, 'Scolaire & Parascolaire', 'parascolaire maternelle');
INSERT INTO public.book_macro_section VALUES (415, 'Faits, temoignages', 'sociologie faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (416, 'Faits, temoignages', 'pamphlets politiques faits de société, témoignages, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (417, 'Faits, temoignages', 'médecine faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (418, 'Faits, temoignages', 'droit faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (419, 'Faits, temoignages', 'histoire faits de société, témoignages contemporains, actualité');
INSERT INTO public.book_macro_section VALUES (420, 'Faits, temoignages', 'psychologie faits de société, témoignages récents, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (421, 'Faits, temoignages', 'sciences appliquées faits de société, témoignages contemporains, actualité, bio');
INSERT INTO public.book_macro_section VALUES (422, 'Faits, temoignages', 'entreprise faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (423, 'Faits, temoignages', 'informatique faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (424, 'Faits, temoignages', 'economie faits de société, témoignages contemporains, actualité, biographies');
INSERT INTO public.book_macro_section VALUES (425, 'Science-fiction, fantastique & terreur', 'science fiction / fantastique grand format');
INSERT INTO public.book_macro_section VALUES (426, 'Science-fiction, fantastique & terreur', 'science fiction / fantastique format poche');
INSERT INTO public.book_macro_section VALUES (427, 'Science-fiction, fantastique & terreur', 'fiction (hors poche) : romans, théâtre, poésie, humour...');
INSERT INTO public.book_macro_section VALUES (428, 'Science-fiction, fantastique & terreur', 'science fiction / fantasy en langue anglaise');
INSERT INTO public.book_macro_section VALUES (429, 'Science-fiction, fantastique & terreur', 'fiction (poche) : romans, théâtre, poésie, humour...');
INSERT INTO public.book_macro_section VALUES (430, 'Science-fiction, fantastique & terreur', 'science fiction / fantastique / terreur revues');
INSERT INTO public.book_macro_section VALUES (431, 'Science-fiction, fantastique & terreur', 'science fiction & terreur');
INSERT INTO public.book_macro_section VALUES (432, 'Science-fiction, fantastique & terreur', 'science fiction / fantastique / terreur audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (433, 'Science-fiction, fantastique & terreur', 'science fiction & terreur (format poche)');
INSERT INTO public.book_macro_section VALUES (434, 'Science-fiction, fantastique & terreur', 'terreur grand format');
INSERT INTO public.book_macro_section VALUES (435, 'Science-fiction, fantastique & terreur', 'terreur format poche');
INSERT INTO public.book_macro_section VALUES (436, 'Loisirs', 'loisirs auto / moto / avions / bateaux / trains');
INSERT INTO public.book_macro_section VALUES (437, 'Loisirs', 'mobilier, antiquités, design, décoration d''intérieur, métiers d''art');
INSERT INTO public.book_macro_section VALUES (438, 'Loisirs', 'jardinage, bricolage, décoration, auto/moto');
INSERT INTO public.book_macro_section VALUES (439, 'Loisirs', 'bricolage, jardinage, décoration, activités manuelles');
INSERT INTO public.book_macro_section VALUES (440, 'Loisirs', 'décoration');
INSERT INTO public.book_macro_section VALUES (441, 'Loisirs', 'jeux revues');
INSERT INTO public.book_macro_section VALUES (442, 'Loisirs', 'activité d''éveil jeunesse');
INSERT INTO public.book_macro_section VALUES (443, 'Loisirs', 'activité d''éveil jeunesse cuisine');
INSERT INTO public.book_macro_section VALUES (444, 'Loisirs', 'activités artistiques adulte');
INSERT INTO public.book_macro_section VALUES (445, 'Loisirs', 'activité jeunesse livres objets tva 5.5');
INSERT INTO public.book_macro_section VALUES (446, 'Loisirs', 'activités artistiques audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (447, 'Loisirs', 'activités artistiques');
INSERT INTO public.book_macro_section VALUES (448, 'Loisirs', 'activités artistiques jeunesse');
INSERT INTO public.book_macro_section VALUES (449, 'Loisirs', 'activité jeunesse jeux coloriages tva 5.5');
INSERT INTO public.book_macro_section VALUES (450, 'Loisirs', 'activité jeunesse jeux coloriages ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (451, 'Loisirs', 'autre activité d''éveil jeunesse');
INSERT INTO public.book_macro_section VALUES (452, 'Loisirs', 'loisirs audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (453, 'Loisirs', 'activité jeunesse audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (454, 'Loisirs', 'activité jeunesse livres objets ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (455, 'Loisirs', 'activités artistiques revues');
INSERT INTO public.book_macro_section VALUES (456, 'Loisirs', 'activité jeunesse 1er âge ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (457, 'Loisirs', 'activité d''éveil jeunesse bricolage et jardinage');
INSERT INTO public.book_macro_section VALUES (458, 'Loisirs', 'loisirs armes');
INSERT INTO public.book_macro_section VALUES (459, 'Loisirs', 'loisirs revues');
INSERT INTO public.book_macro_section VALUES (460, 'Loisirs', 'activité jeunesse revues');
INSERT INTO public.book_macro_section VALUES (461, 'Loisirs', 'art de vie, mode');
INSERT INTO public.book_macro_section VALUES (462, 'Loisirs', 'musique');
INSERT INTO public.book_macro_section VALUES (463, 'Loisirs', 'photo');
INSERT INTO public.book_macro_section VALUES (464, 'Loisirs', 'bricolage');
INSERT INTO public.book_macro_section VALUES (465, 'Policier ', 'policier / thriller format poche');
INSERT INTO public.book_macro_section VALUES (466, 'Policier ', 'policier / thriller grand format');
INSERT INTO public.book_macro_section VALUES (467, 'Policier ', 'policier / suspense / espionnage en langue anglaise');
INSERT INTO public.book_macro_section VALUES (468, 'Policier ', 'policier revues');
INSERT INTO public.book_macro_section VALUES (469, 'Policier ', 'policier & thriller');
INSERT INTO public.book_macro_section VALUES (470, 'Policier ', 'policier audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (471, 'Policier ', 'policier & thriller (format poche)');
INSERT INTO public.book_macro_section VALUES (472, 'Gestion/entreprise', 'développement personnel');
INSERT INTO public.book_macro_section VALUES (473, 'Gestion/entreprise', 'création d''entreprise');
INSERT INTO public.book_macro_section VALUES (474, 'Gestion/entreprise', 'poche entreprise');
INSERT INTO public.book_macro_section VALUES (475, 'Gestion/entreprise', 'entreprise');
INSERT INTO public.book_macro_section VALUES (476, 'Gestion/entreprise', 'entreprise audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (477, 'Gestion/entreprise', 'management et ressources humaines');
INSERT INTO public.book_macro_section VALUES (478, 'Gestion/entreprise', 'stratégie de l''entreprise');
INSERT INTO public.book_macro_section VALUES (479, 'Gestion/entreprise', 'organisation des entreprises');
INSERT INTO public.book_macro_section VALUES (480, 'Gestion/entreprise', 'contrôle de gestion');
INSERT INTO public.book_macro_section VALUES (481, 'Jeux', 'jeux audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (482, 'Jeux', 'jeux');
INSERT INTO public.book_macro_section VALUES (483, 'Jeux', 'jeux divers');
INSERT INTO public.book_macro_section VALUES (484, 'Jeux', 'logiciel jeux');
INSERT INTO public.book_macro_section VALUES (485, 'Jeux', 'jeux de société');
INSERT INTO public.book_macro_section VALUES (486, 'Jeux', 'jeux de rôle');
INSERT INTO public.book_macro_section VALUES (487, 'Vie pratique ', 'vie pratique & loisirs');
INSERT INTO public.book_macro_section VALUES (488, 'Vie pratique ', 'randonnée survie');
INSERT INTO public.book_macro_section VALUES (489, 'Vie pratique ', 'la vie après la mort');
INSERT INTO public.book_macro_section VALUES (490, 'Vie pratique ', 'vie pratique en langue anglaise');
INSERT INTO public.book_macro_section VALUES (491, 'Vie pratique ', 'vie pratique en langue allemande');
INSERT INTO public.book_macro_section VALUES (492, 'Vie pratique ', 'logiciel vie pratique');
INSERT INTO public.book_macro_section VALUES (493, 'Sport', 'sports, equitation, tauromachie');
INSERT INTO public.book_macro_section VALUES (494, 'Sport', 'sports');
INSERT INTO public.book_macro_section VALUES (495, 'Sport', 'sports revues');
INSERT INTO public.book_macro_section VALUES (496, 'Sport', 'sports audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (497, 'Sport', 'sports mécaniques');
INSERT INTO public.book_macro_section VALUES (498, 'Sport', 'sports collectifs');
INSERT INTO public.book_macro_section VALUES (499, 'Sport', 'sports de montagne');
INSERT INTO public.book_macro_section VALUES (500, 'Sport', 'sports individuels');
INSERT INTO public.book_macro_section VALUES (501, 'Sport', 'sports nautiques');
INSERT INTO public.book_macro_section VALUES (502, 'Sport', 'sports chasse / pêche');
INSERT INTO public.book_macro_section VALUES (503, 'Sport', 'arts martiaux');
INSERT INTO public.book_macro_section VALUES (504, 'Sport', 'gymnastique / sports d''entretien physique / danse');
INSERT INTO public.book_macro_section VALUES (505, 'Sport', 'danses et autres spectacles');
INSERT INTO public.book_macro_section VALUES (506, 'Géographie, cartographie', 'géographie revues');
INSERT INTO public.book_macro_section VALUES (507, 'Géographie, cartographie', 'géographie, démographie, transports');
INSERT INTO public.book_macro_section VALUES (508, 'Géographie, cartographie', 'géographie de la france');
INSERT INTO public.book_macro_section VALUES (509, 'Géographie, cartographie', 'poche géographie');
INSERT INTO public.book_macro_section VALUES (510, 'Géographie, cartographie', 'géographie audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (511, 'Géographie, cartographie', 'géographie essais et études');
INSERT INTO public.book_macro_section VALUES (512, 'Géographie, cartographie', 'cartographie');
INSERT INTO public.book_macro_section VALUES (513, 'Géographie, cartographie', 'géographie de l''europe');
INSERT INTO public.book_macro_section VALUES (514, 'Géographie, cartographie', 'démographie');
INSERT INTO public.book_macro_section VALUES (515, 'Géographie, cartographie', 'histoire autres continents');
INSERT INTO public.book_macro_section VALUES (516, 'Géographie, cartographie', 'géographie autres continents');
INSERT INTO public.book_macro_section VALUES (517, 'Religions, spiritualitées', 'franc-maçonnerie / occultisme / symbolisme');
INSERT INTO public.book_macro_section VALUES (518, 'Religions, spiritualitées', 'religion revues');
INSERT INTO public.book_macro_section VALUES (519, 'Religions, spiritualitées', 'esotérisme revues');
INSERT INTO public.book_macro_section VALUES (520, 'Religions, spiritualitées', 'religion');
INSERT INTO public.book_macro_section VALUES (521, 'Religions, spiritualitées', 'poche religion');
INSERT INTO public.book_macro_section VALUES (522, 'Religions, spiritualitées', 'religion audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (523, 'Religions, spiritualitées', 'phénomènes paranormaux et extraordinaires');
INSERT INTO public.book_macro_section VALUES (524, 'Religions, spiritualitées', 'maîtres spirituels / spiritualité');
INSERT INTO public.book_macro_section VALUES (525, 'Religions, spiritualitées', 'islam');
INSERT INTO public.book_macro_section VALUES (526, 'Religions, spiritualitées', 'orientalisme / bouddhisme / hindouisme');
INSERT INTO public.book_macro_section VALUES (527, 'Religions, spiritualitées', 'christianisme : essais religieux, témoignages, biographies');
INSERT INTO public.book_macro_section VALUES (528, 'Religions, spiritualitées', 'christianisme : dictionnaires et théologie');
INSERT INTO public.book_macro_section VALUES (529, 'Religions, spiritualitées', 'judaïsme');
INSERT INTO public.book_macro_section VALUES (530, 'Religions, spiritualitées', 'spiritualité, esotérisme, religion');
INSERT INTO public.book_macro_section VALUES (531, 'Religions, spiritualitées', 'biblesesotérisme');
INSERT INTO public.book_macro_section VALUES (532, 'Religions, spiritualitées', 'poche esotérisme');
INSERT INTO public.book_macro_section VALUES (533, 'Religions, spiritualitées', 'esotérisme audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (534, 'Religions, spiritualitées', 'arts divinatoires');
INSERT INTO public.book_macro_section VALUES (535, 'Psychanalyse, psychologie', 'psychologie et psychanalyse poche');
INSERT INTO public.book_macro_section VALUES (536, 'Psychanalyse, psychologie', 'psychologie et psychanalyse audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (537, 'Psychanalyse, psychologie', 'psychologie et psychanalyse');
INSERT INTO public.book_macro_section VALUES (538, 'Psychanalyse, psychologie', 'psychologie de l''enfant');
INSERT INTO public.book_macro_section VALUES (539, 'Psychanalyse, psychologie', 'psychologie / psychothérapie');
INSERT INTO public.book_macro_section VALUES (540, 'Psychanalyse, psychologie', 'psychanalyse');
INSERT INTO public.book_macro_section VALUES (541, 'Psychanalyse, psychologie', 'psychologie et psychanalyse revues');
INSERT INTO public.book_macro_section VALUES (542, 'Psychanalyse, psychologie', 'caractérologie graphologie morphologie');
INSERT INTO public.book_macro_section VALUES (543, 'Manga', 'mangas / manwha / man hua');
INSERT INTO public.book_macro_section VALUES (544, 'Carrière/Concours', 'carrières et emplois concours (hors professorat et paramédical)');
INSERT INTO public.book_macro_section VALUES (545, 'Carrière/Concours', 'carrières et emplois');
INSERT INTO public.book_macro_section VALUES (546, 'Carrière/Concours', 'carrières et emplois audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (547, 'Carrière/Concours', 'pédagogie pour l''enseignement, concours professorat');
INSERT INTO public.book_macro_section VALUES (548, 'Carrière/Concours', 'recherche d''emploi');
INSERT INTO public.book_macro_section VALUES (549, 'Carrière/Concours', 'paramédical concours (infirmier, aide soignant, kiné, podologue, ...)');
INSERT INTO public.book_macro_section VALUES (550, 'Carrière/Concours', 'carrière, travail, education');
INSERT INTO public.book_macro_section VALUES (551, 'Carrière/Concours', 'conjugaison, grammaire, orthographe');
INSERT INTO public.book_macro_section VALUES (552, 'Carrière/Concours', 'carrières et emplois revues');
INSERT INTO public.book_macro_section VALUES (553, 'Marketing et audio-visuel', 'architecture, urbanisme, packaging, publicité');
INSERT INTO public.book_macro_section VALUES (554, 'Marketing et audio-visuel', 'cinéma, télévision, audiovisuel, presse, médias');
INSERT INTO public.book_macro_section VALUES (555, 'Marketing et audio-visuel', 'marketing, commercial, publicité');
INSERT INTO public.book_macro_section VALUES (556, 'Santé', 'santé & bien-être');
INSERT INTO public.book_macro_section VALUES (557, 'Santé', 'flore et composition florale');
INSERT INTO public.book_macro_section VALUES (558, 'Santé', 'maternité, paternité, enfance');
INSERT INTO public.book_macro_section VALUES (559, 'Santé', 'vins et boissons');
INSERT INTO public.book_macro_section VALUES (560, 'Santé', 'autres thèmes de santé');
INSERT INTO public.book_macro_section VALUES (561, 'Santé', 'poche santé');
INSERT INTO public.book_macro_section VALUES (562, 'Santé', 'santé audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (563, 'Santé', 'santé');
INSERT INTO public.book_macro_section VALUES (564, 'Santé', 'aides soignants');
INSERT INTO public.book_macro_section VALUES (565, 'Santé', 'arbres et arbustes');
INSERT INTO public.book_macro_section VALUES (566, 'Santé', 'alimentation, diététique, régimes');
INSERT INTO public.book_macro_section VALUES (567, 'Santé', 'infirmiers');
INSERT INTO public.book_macro_section VALUES (568, 'Santé', 'autres spécialités médicales');
INSERT INTO public.book_macro_section VALUES (569, 'Santé', 'kinés/podologues/ostéopathes');
INSERT INTO public.book_macro_section VALUES (570, 'Santé', 'orthophonie et autres spécialités');
INSERT INTO public.book_macro_section VALUES (571, 'Santé', 'chirurgie / traumatologie');
INSERT INTO public.book_macro_section VALUES (572, 'Santé', 'homéopathie et autres médecines douces');
INSERT INTO public.book_macro_section VALUES (573, 'Santé', 'vétérinaire');
INSERT INTO public.book_macro_section VALUES (574, 'Santé', 'puériculture');
INSERT INTO public.book_macro_section VALUES (575, 'Santé', 'paramédical');
INSERT INTO public.book_macro_section VALUES (576, 'Santé', 'paramédical audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (577, 'Santé', 'soutien maternelle');
INSERT INTO public.book_macro_section VALUES (578, 'Santé', 'soins dentaires / stomatologie');
INSERT INTO public.book_macro_section VALUES (579, 'Santé', 'pédiatrie');
INSERT INTO public.book_macro_section VALUES (580, 'Santé', 'radiologie / imagerie');
INSERT INTO public.book_macro_section VALUES (581, 'Santé', 'pédagogie revues');
INSERT INTO public.book_macro_section VALUES (582, 'Humour', 'humour grand format');
INSERT INTO public.book_macro_section VALUES (583, 'Humour', 'humour format poche');
INSERT INTO public.book_macro_section VALUES (584, 'Humour', 'humour audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (585, 'Humour', 'humour');
INSERT INTO public.book_macro_section VALUES (586, 'Humour', 'humour revues');
INSERT INTO public.book_macro_section VALUES (587, 'Sociologie', 'essais de sociologie');
INSERT INTO public.book_macro_section VALUES (588, 'Sociologie', 'sociologie');
INSERT INTO public.book_macro_section VALUES (589, 'Sociologie', 'sociologie audio vidéo ou produits tva 20');
INSERT INTO public.book_macro_section VALUES (590, 'Sociologie', 'action sociale');
INSERT INTO public.book_macro_section VALUES (591, 'Sociologie', 'sociologie traités/textes/auteurs fondamentaux');
INSERT INTO public.book_macro_section VALUES (592, 'Sociologie', 'sociologie revues');
INSERT INTO public.book_macro_section VALUES (593, 'Sociologie', 'ethnologie et anthropologie');


--
-- Data for Name: booking; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: boost_cinema_details; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: business_unit; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: business_unit_venue_link; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cashflow; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cashflow_batch; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cashflow_log; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cashflow_pricing; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cds_cinema_details; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: cinema_provider_pivot; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_booking; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_offer; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_offer_domain; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_offer_template; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_offer_template_domain; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: collective_stock; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: criterion; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.criterion VALUES (1, 'Bonne offre d’appel', 'Offre déjà beaucoup réservée par les autres jeunes', NULL, NULL);
INSERT INTO public.criterion VALUES (2, 'Mauvaise accroche', 'Offre ne possèdant pas une accroche de qualité suffisante', NULL, NULL);
INSERT INTO public.criterion VALUES (3, 'Offre de médiation spécifique', 'Offre possédant une médiation orientée pour les jeunes de 18 ans', NULL, NULL);


--
-- Data for Name: custom_reimbursement_rule; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: deposit; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_deposit; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_domain; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_domain_venue; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_institution; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_redactor; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: educational_year; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: external_booking; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: favorite; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: feature; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.feature VALUES (1, 'ENABLE_PHONE_VALIDATION', 'Active la validation du numéro de téléphone', true);
INSERT INTO public.feature VALUES (3, 'ENABLE_IDCHECK_FRAUD_CONTROLS', 'Active les contrôles de sécurité en sortie du process ID Check', true);
INSERT INTO public.feature VALUES (4, 'DISPLAY_DMS_REDIRECTION', 'Affiche une redirection vers DMS si ID Check est KO', true);
INSERT INTO public.feature VALUES (5, 'ENABLE_NEW_VENUE_PAGES', 'Utiliser la nouvelle version des pages d''edition et de creation de lieux', false);
INSERT INTO public.feature VALUES (6, 'ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING', 'Active le mode debug Firebase pour l''Id Check intégrée à l''application native', false);
INSERT INTO public.feature VALUES (8, 'ENABLE_ISBN_REQUIRED_IN_LIVRE_EDITION_OFFER_CREATION', 'Active le champ isbn obligatoire lors de la création d''offre de type LIVRE_EDITION', false);
INSERT INTO public.feature VALUES (9, 'ID_CHECK_ADDRESS_AUTOCOMPLETION', 'Autocomplétion de l''adresse lors du parcours IDCheck', false);
INSERT INTO public.feature VALUES (10, 'USER_PROFILING_FRAUD_CHECK', 'Détection de la fraude basée sur le profil de l''utilisateur', false);
INSERT INTO public.feature VALUES (11, 'BENEFICIARY_VALIDATION_AFTER_FRAUD_CHECKS', 'Active la validation d''un bénéficiaire via les contrôles de sécurité', true);
INSERT INTO public.feature VALUES (12, 'WEBAPP_V2_ENABLED', 'Utiliser la nouvelle web app (décli web/v2) au lieu de l''ancienne', true);
INSERT INTO public.feature VALUES (13, 'PRICE_BOOKINGS', 'Active la valorisation des réservations', true);
INSERT INTO public.feature VALUES (14, 'GENERATE_CASHFLOWS_BY_CRON', 'Active la génération automatique (via cron) des flux monétaires et fichiers de remboursement', false);
INSERT INTO public.feature VALUES (15, 'ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18', 'Permet l''affichage du lien vers DMS sur la page de maintenance pour les 18 ans', true);
INSERT INTO public.feature VALUES (16, 'API_SIRENE_AVAILABLE', 'Active les fonctionnalitées liées à l''API Sirene', true);
INSERT INTO public.feature VALUES (17, 'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION', 'Permettre limport journalier des résumés des livres', true);
INSERT INTO public.feature VALUES (18, 'ENABLE_VENUE_STRICT_SEARCH', 'Active le fait d''indiquer si un lieu a un moins une offre éligible lors de l''indexation (Algolia)', true);
INSERT INTO public.feature VALUES (19, 'ENABLE_NEW_IDENTIFICATION_FLOW', 'Activer le nouveau flux d''inscription jeune pré-Ubble', false);
INSERT INTO public.feature VALUES (20, 'ENABLE_NATIVE_APP_RECAPTCHA', 'Active le reCaptacha sur l''API native', true);
INSERT INTO public.feature VALUES (21, 'ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION', 'Active l''utilisation du lien avec redirection pour les offres (nécessaires pour contourner des restrictions d''iOS)', false);
INSERT INTO public.feature VALUES (22, 'ENABLE_EAC_FINANCIAL_PROTECTION', 'Protege le pass culture contre les ministeres qui dépenseraient plus que leur budget sur les 4 derniers mois de l''année', false);
INSERT INTO public.feature VALUES (23, 'SYNCHRONIZE_ALLOCINE', 'Permettre la synchronisation journalière avec Allociné', true);
INSERT INTO public.feature VALUES (24, 'USE_PRICING_POINT_FOR_PRICING', 'Utilise le modèle VenuePricingPointLink pour la valorisation', false);
INSERT INTO public.feature VALUES (25, 'ENABLE_BOOST_API_INTEGRATION', 'Active la réservation de places de cinéma via l''API Boost', false);
INSERT INTO public.feature VALUES (26, 'ENABLE_PRO_ACCOUNT_CREATION', 'Permettre l''inscription des comptes professionels', true);
INSERT INTO public.feature VALUES (28, 'ENABLE_PRO_BOOKINGS_V2', 'Activer l''affichage de la page booking avec la nouvelle architecture.', false);
INSERT INTO public.feature VALUES (29, 'UPDATE_BOOKING_USED', 'Permettre la validation automatique des contremarques 48h après la fin de lévènement', true);
INSERT INTO public.feature VALUES (30, 'ENABLE_UBBLE_SUBSCRIPTION_LIMITATION', 'Active la limitation en fonction de l''âge lors de pic d''inscription', false);
INSERT INTO public.feature VALUES (31, 'ENABLE_USER_PROFILING', 'Active l''étape USER_PROFILING dans le parcours d''inscription des jeunes de 18 ans', false);
INSERT INTO public.feature VALUES (32, 'TEMP_ENABLE_JOB_HIGHLIGHTS_BANNER', 'Activer la bannière pour les Temps forts métiers', false);
INSERT INTO public.feature VALUES (33, 'ENABLE_PRO_NEW_VENUE_PROVIDER_UI', 'Activer le nouveau affichage de la section synchronisation sur la page lieu', true);
INSERT INTO public.feature VALUES (34, 'INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS', 'Inclure les anciens modèles de données pour le téléchargement des remboursements ', true);
INSERT INTO public.feature VALUES (35, 'DISABLE_ENTERPRISE_API', 'Désactiver les appels à l''API entreprise', false);
INSERT INTO public.feature VALUES (36, 'ENABLE_OFFERER_STATS', 'Active l''affichage des statistiques d''une structure sur le portail pro', false);
INSERT INTO public.feature VALUES (37, 'ALLOW_IDCHECK_REGISTRATION', 'Autoriser les utilisateurs de 18 ans à suivre le parcours d inscription ID Check', true);
INSERT INTO public.feature VALUES (38, 'SYNCHRONIZE_TITELIVE_PRODUCTS', 'Permettre limport journalier du référentiel des livres', true);
INSERT INTO public.feature VALUES (39, 'APP_ENABLE_COOKIES_V2', 'Activer la gestion conforme des cookies', false);
INSERT INTO public.feature VALUES (40, 'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS', 'Permettre limport journalier des couvertures de livres', true);
INSERT INTO public.feature VALUES (41, 'USE_INSEE_SIRENE_API', 'Utiliser la nouvelle API Sirene de l''Insee', true);
INSERT INTO public.feature VALUES (42, 'ALLOW_IDCHECK_UNDERAGE_REGISTRATION', 'Autoriser les utilisateurs de moins de 15 à 17 ans à suivre le parcours d inscription ID Check', true);
INSERT INTO public.feature VALUES (43, 'DISABLE_STORE_REVIEW', 'Désactive la demande de notation sur les stores à la suite d’une réservation', false);
INSERT INTO public.feature VALUES (44, 'ENABLE_CDS_IMPLEMENTATION', 'Permet la réservation de place de cinéma avec l''API CDS', false);
INSERT INTO public.feature VALUES (45, 'ENABLE_FRONT_IMAGE_RESIZING', 'Active le redimensionnement sur demande des images par l''app et le web', false);
INSERT INTO public.feature VALUES (46, 'ENABLE_CSV_MULTI_DOWNLOAD_BUTTON', 'Active le multi-téléchargement des réservations', true);
INSERT INTO public.feature VALUES (47, 'WIP_IMAGE_COLLECTIVE_OFFER', 'Active les images dans les offres collectives et les offres vitrines.', false);
INSERT INTO public.feature VALUES (48, 'ENFORCE_BANK_INFORMATION_WITH_SIRET', 'Forcer les informations banquaires à être liées à un SIRET.', false);
INSERT INTO public.feature VALUES (49, 'ENABLE_CULTURAL_SURVEY', 'Activer l''affichage du questionnaire des pratiques initiales pour les bénéficiaires', false);
INSERT INTO public.feature VALUES (50, 'ENABLE_NEW_BANK_INFORMATIONS_CREATION', 'Active le nouveau parcours d''ajout de coordonnées bancaires sur la page lieu', true);
INSERT INTO public.feature VALUES (51, 'ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE', 'Permet l''affichage du lien vers DMS sur la page de maintenance pour les 15-17 ans', false);
INSERT INTO public.feature VALUES (52, 'USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS', 'Utilise le modèle VenueReimbursementPointLink pour les cashflows', false);
INSERT INTO public.feature VALUES (53, 'ENABLE_ZENDESK_SELL_CREATION', 'Activer la création de nouvelles entrées dans Zendesk Sell (structures et lieux)', false);
INSERT INTO public.feature VALUES (54, 'PRO_DISABLE_EVENTS_QRCODE', 'Active la possibilité de différencier le type d’envoi des billets sur une offre et le retrait du QR code sur la réservation', false);
INSERT INTO public.feature VALUES (55, 'WIP_ENABLE_BACKOFFICE_V3', 'Autorise l''accès au nouveau back-office (v3)', false);
INSERT INTO public.feature VALUES (56, 'TEMP_DISABLE_OFFERER_VALIDATION_EMAIL', 'Désactiver l''envoi d''email interne de validation par token pour les structures et rattachements', false);
INSERT INTO public.feature VALUES (57, 'OFFER_FORM_V3', 'Afficher la version 3 du formulaire d''offre', false);
INSERT INTO public.feature VALUES (58, 'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION', 'Active l''écran carrefour sur la page de choix du type d’offre à créer, afin de pouvoir créer une offre collective vitrine dès le départ', false);
INSERT INTO public.feature VALUES (59, 'ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE', 'Autoriser la redirection vers Ubble (en backup) pour les utilisateurs éligibles à éduconnect', false);
INSERT INTO public.feature VALUES (60, 'ENABLE_UBBLE', 'Active la vérification d''identité par Ubble', true);
INSERT INTO public.feature VALUES (61, 'ENABLE_DUPLICATE_USER_RULE_WITHOUT_BIRTHDATE', 'Utiliser la nouvelle règle de détection d''utilisateur en doublon', false);
INSERT INTO public.feature VALUES (62, 'APP_ENABLE_AUTOCOMPLETE', 'Active l''autocomplete sur la barre de recherche relative au rework de la homepage', true);
INSERT INTO public.feature VALUES (63, 'ENABLE_NEW_BOOKING_FILTERS', 'Active les nouveaux filtres sur les statuts pour la page de réservations', true);
INSERT INTO public.feature VALUES (64, 'ENABLE_NATIVE_CULTURAL_SURVEY', 'Active le Questionnaire des pratiques initiales natif (non TypeForm) sur l''app native et décli web', true);
INSERT INTO public.feature VALUES (65, 'VENUE_FORM_V2', 'Afficher la version 2 du formulaire de lieu', false);
INSERT INTO public.feature VALUES (66, 'ENABLE_AUTO_VALIDATION_FOR_EXTERNAL_BOOKING', 'Valide automatiquement après 48h les offres issues de l''api billeterie cinéma', false);
INSERT INTO public.feature VALUES (67, 'DISABLE_USER_NAME_AND_FIRST_NAME_VALIDATION_IN_TESTING_AND_STAGING', 'Désactiver la validation des noms et prénoms', true);
INSERT INTO public.feature VALUES (68, 'ENABLE_EDUCONNECT_AUTHENTICATION', 'Active l''authentification via educonnect sur l''app native', true);


--
-- Data for Name: individual_booking; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: invoice; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: invoice_cashflow; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: invoice_line; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: latest_dms_import; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: local_provider_event; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: mediation; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offer; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offer_criterion; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offer_report; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offer_validation_config; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offerer; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: offerer_tag; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.offerer_tag VALUES (1, 'top-acteur', 'Top Acteur', 'Acteur prioritaire dans les objectifs d''acquisition', NULL);


--
-- Data for Name: offerer_tag_mapping; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: orphan_dms_application; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: payment_message; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: payment_status; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: pricing; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: pricing_line; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: pricing_log; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: provider; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.provider VALUES (false, 1, 'TiteLive (Epagine / Place des libraires.com)', 'TiteLiveThings', false, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (false, 2, 'TiteLive (Epagine / Place des libraires.com) Descriptions', 'TiteLiveThingDescriptions', false, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (false, 3, 'TiteLive (Epagine / Place des libraires.com) Thumbs', 'TiteLiveThingThumbs', false, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (false, 4, 'Allociné', 'AllocineStocks', false, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (false, 5, 'FNAC', 'FnacStocks', false, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (true, 6, 'Ciné Office', 'CDSStocks', true, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (true, 7, 'Boost', 'BoostStocks', true, NULL, NULL, false, false);
INSERT INTO public.provider VALUES (false, 8, 'Pass Culture API Stocks', 'PCAPIStocks', false, NULL, NULL, false, false);


--
-- Data for Name: recredit; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: reference_scheme; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.reference_scheme VALUES (1, 'invoice.reference', 'F', 2022, 1, 7);
INSERT INTO public.reference_scheme VALUES (2, 'invoice.reference', 'F', 2023, 1, 7);
INSERT INTO public.reference_scheme VALUES (3, 'invoice.reference', 'F', 2024, 1, 7);
INSERT INTO public.reference_scheme VALUES (4, 'invoice.reference', 'F', 2025, 1, 7);
INSERT INTO public.reference_scheme VALUES (5, 'invoice.reference', 'F', 2026, 1, 7);


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.role VALUES (1, 'admin');


--
-- Data for Name: role_backoffice_profile; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: role_permission; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.role_permission VALUES (1, NULL, 1);


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: stock; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: token; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: transaction; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: user_email_history; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: user_offerer; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: user_session; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: user_suspension; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_contact; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_criterion; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_educational_status; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_label; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_pricing_point_link; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_provider; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_reimbursement_point_link; Type: TABLE DATA; Schema: public; Owner: pass_culture
--



--
-- Data for Name: venue_type; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.venue_type VALUES (1, 'Arts visuels, arts plastiques et galeries');
INSERT INTO public.venue_type VALUES (2, 'Centre culturel');
INSERT INTO public.venue_type VALUES (3, 'Cours et pratique artistiques');
INSERT INTO public.venue_type VALUES (4, 'Culture scientifique');
INSERT INTO public.venue_type VALUES (5, 'Festival');
INSERT INTO public.venue_type VALUES (6, 'Jeux / Jeux vidéos');
INSERT INTO public.venue_type VALUES (7, 'Librairie');
INSERT INTO public.venue_type VALUES (8, 'Bibliothèque ou médiathèque');
INSERT INTO public.venue_type VALUES (9, 'Musée');
INSERT INTO public.venue_type VALUES (10, 'Musique - Disquaire');
INSERT INTO public.venue_type VALUES (11, 'Musique - Magasin d’instruments');
INSERT INTO public.venue_type VALUES (12, 'Musique - Salle de concerts');
INSERT INTO public.venue_type VALUES (13, 'Offre numérique');
INSERT INTO public.venue_type VALUES (14, 'Patrimoine et tourisme');
INSERT INTO public.venue_type VALUES (15, 'Cinéma - Salle de projections');
INSERT INTO public.venue_type VALUES (16, 'Spectacle vivant');
INSERT INTO public.venue_type VALUES (17, 'Autre');


--
-- Data for Name: geocode_settings; Type: TABLE DATA; Schema: tiger; Owner: pass_culture
--



--
-- Data for Name: pagc_gaz; Type: TABLE DATA; Schema: tiger; Owner: pass_culture
--



--
-- Data for Name: pagc_lex; Type: TABLE DATA; Schema: tiger; Owner: pass_culture
--



--
-- Data for Name: pagc_rules; Type: TABLE DATA; Schema: tiger; Owner: pass_culture
--



--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: pass_culture
--



--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: pass_culture
--



--
-- Name: action_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.action_history_id_seq', 1, false);


--
-- Name: activation_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.activation_code_id_seq', 1, false);


--
-- Name: activity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.activity_id_seq', 1, false);


--
-- Name: allocine_pivot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.allocine_pivot_id_seq', 1, false);


--
-- Name: allocine_theater_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.allocine_theater_id_seq', 1, false);


--
-- Name: allocine_venue_provider_price_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.allocine_venue_provider_price_rule_id_seq', 1, false);


--
-- Name: api_key_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.api_key_id_seq', 1, false);


--
-- Name: backoffice_user_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.backoffice_user_profile_id_seq', 1, false);


--
-- Name: bank_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.bank_information_id_seq', 1, false);


--
-- Name: beneficiary_fraud_check_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_fraud_check_id_seq', 1, false);


--
-- Name: beneficiary_fraud_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_fraud_review_id_seq', 1, false);


--
-- Name: beneficiary_import_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_import_id_seq', 1, false);


--
-- Name: beneficiary_import_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_import_status_id_seq', 1, false);


--
-- Name: book_macro_section_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.book_macro_section_id_seq', 593, true);


--
-- Name: booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.booking_id_seq', 1, false);


--
-- Name: boost_cinema_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.boost_cinema_details_id_seq', 1, false);


--
-- Name: business_unit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.business_unit_id_seq', 1, false);


--
-- Name: business_unit_venue_link_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.business_unit_venue_link_id_seq', 1, false);


--
-- Name: cashflow_batch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.cashflow_batch_id_seq', 1, false);


--
-- Name: cashflow_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.cashflow_id_seq', 1, false);


--
-- Name: cashflow_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.cashflow_log_id_seq', 1, false);


--
-- Name: cds_cinema_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.cds_cinema_details_id_seq', 1, false);


--
-- Name: cinema_provider_pivot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.cinema_provider_pivot_id_seq', 1, false);


--
-- Name: collective_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.collective_booking_id_seq', 1, false);


--
-- Name: collective_offer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.collective_offer_id_seq', 1, false);


--
-- Name: collective_offer_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.collective_offer_template_id_seq', 1, false);


--
-- Name: collective_stock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.collective_stock_id_seq', 1, false);


--
-- Name: criterion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.criterion_id_seq', 3, true);


--
-- Name: custom_reimbursement_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.custom_reimbursement_rule_id_seq', 1, false);


--
-- Name: deposit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.deposit_id_seq', 1, false);


--
-- Name: educational_deposit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_deposit_id_seq', 1, false);


--
-- Name: educational_domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_domain_id_seq', 1, false);


--
-- Name: educational_domain_venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_domain_venue_id_seq', 1, false);


--
-- Name: educational_institution_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_institution_id_seq', 1, false);


--
-- Name: educational_redactor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_redactor_id_seq', 1, false);


--
-- Name: educational_year_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.educational_year_id_seq', 1, false);


--
-- Name: external_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.external_booking_id_seq', 1, false);


--
-- Name: favorite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.favorite_id_seq', 1, false);


--
-- Name: feature_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.feature_id_seq', 68, true);


--
-- Name: individual_booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.individual_booking_id_seq', 1, false);


--
-- Name: invoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.invoice_id_seq', 1, false);


--
-- Name: invoice_line_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.invoice_line_id_seq', 1, false);


--
-- Name: latest_dms_import_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.latest_dms_import_id_seq', 1, false);


--
-- Name: local_provider_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.local_provider_event_id_seq', 1, false);


--
-- Name: mediation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.mediation_id_seq', 1, false);


--
-- Name: offer_criterion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offer_criterion_id_seq', 1, false);


--
-- Name: offer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offer_id_seq', 1, false);


--
-- Name: offer_report_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offer_report_id_seq', 1, false);


--
-- Name: offer_validation_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offer_validation_config_id_seq', 1, false);


--
-- Name: offerer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offerer_id_seq', 1, false);


--
-- Name: offerer_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offerer_tag_id_seq', 1, true);


--
-- Name: offerer_tag_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offerer_tag_mapping_id_seq', 1, false);


--
-- Name: orphan_dms_application_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.orphan_dms_application_id_seq', 1, false);


--
-- Name: payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.payment_id_seq', 1, false);


--
-- Name: payment_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.payment_message_id_seq', 1, false);


--
-- Name: payment_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.payment_status_id_seq', 1, false);


--
-- Name: permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.permission_id_seq', 1, true);


--
-- Name: pricing_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.pricing_id_seq', 1, false);


--
-- Name: pricing_line_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.pricing_line_id_seq', 1, false);


--
-- Name: pricing_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.pricing_log_id_seq', 1, false);


--
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.product_id_seq', 1, false);


--
-- Name: provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.provider_id_seq', 10, true);


--
-- Name: recredit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.recredit_id_seq', 1, false);


--
-- Name: reference_scheme_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.reference_scheme_id_seq', 5, true);


--
-- Name: role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.role_id_seq', 1, true);


--
-- Name: role_permission_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.role_permission_seq', 1, true);


--
-- Name: stock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.stock_id_seq', 1, false);


--
-- Name: token_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.token_id_seq', 1, false);


--
-- Name: transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.transaction_id_seq', 1, false);


--
-- Name: user_email_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.user_email_history_id_seq', 1, false);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.user_id_seq', 1, false);


--
-- Name: user_offerer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.user_offerer_id_seq', 1, false);


--
-- Name: user_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.user_session_id_seq', 1, false);


--
-- Name: user_suspension_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.user_suspension_id_seq', 1, false);


--
-- Name: venue_contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_contact_id_seq', 1, false);


--
-- Name: venue_criterion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_criterion_id_seq', 1, false);


--
-- Name: venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_id_seq', 1, false);


--
-- Name: venue_label_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_label_id_seq', 1, false);


--
-- Name: venue_pricing_point_link_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_pricing_point_link_id_seq', 1, false);


--
-- Name: venue_provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_provider_id_seq', 1, false);


--
-- Name: venue_reimbursement_point_link_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_reimbursement_point_link_id_seq', 1, false);


--
-- Name: venue_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_type_id_seq', 17, true);


--
-- Name: action_history action_history_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history
    ADD CONSTRAINT action_history_pkey PRIMARY KEY (id);


--
-- Name: activation_code activation_code_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activation_code
    ADD CONSTRAINT activation_code_pkey PRIMARY KEY (id);


--
-- Name: allocine_pivot allocine_pivot_internalId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT "allocine_pivot_internalId_key" UNIQUE ("internalId");


--
-- Name: allocine_pivot allocine_pivot_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT allocine_pivot_pkey PRIMARY KEY (id);


--
-- Name: allocine_pivot allocine_pivot_theaterId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT "allocine_pivot_theaterId_key" UNIQUE ("theaterId");


--
-- Name: allocine_pivot allocine_pivot_venueId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT "allocine_pivot_venueId_key" UNIQUE ("venueId");


--
-- Name: allocine_theater allocine_theater_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_theater
    ADD CONSTRAINT allocine_theater_pkey PRIMARY KEY (id);


--
-- Name: allocine_venue_provider allocine_venue_provider_internalId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider
    ADD CONSTRAINT "allocine_venue_provider_internalId_key" UNIQUE ("internalId");


--
-- Name: allocine_venue_provider allocine_venue_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider
    ADD CONSTRAINT allocine_venue_provider_pkey PRIMARY KEY (id);


--
-- Name: allocine_venue_provider_price_rule allocine_venue_provider_price_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider_price_rule
    ADD CONSTRAINT allocine_venue_provider_price_rule_pkey PRIMARY KEY (id);


--
-- Name: api_key api_key_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.api_key
    ADD CONSTRAINT api_key_pkey PRIMARY KEY (id);


--
-- Name: api_key api_key_prefix_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.api_key
    ADD CONSTRAINT api_key_prefix_key UNIQUE (prefix);


--
-- Name: backoffice_user_profile backoffice_user_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.backoffice_user_profile
    ADD CONSTRAINT backoffice_user_profile_pkey PRIMARY KEY (id);


--
-- Name: bank_information bank_information_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information
    ADD CONSTRAINT bank_information_pkey PRIMARY KEY (id);


--
-- Name: beneficiary_fraud_check beneficiary_fraud_check_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_check
    ADD CONSTRAINT beneficiary_fraud_check_pkey PRIMARY KEY (id);


--
-- Name: beneficiary_fraud_review beneficiary_fraud_review_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_review
    ADD CONSTRAINT beneficiary_fraud_review_pkey PRIMARY KEY (id);


--
-- Name: beneficiary_import beneficiary_import_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import
    ADD CONSTRAINT beneficiary_import_pkey PRIMARY KEY (id);


--
-- Name: beneficiary_import_status beneficiary_import_status_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import_status
    ADD CONSTRAINT beneficiary_import_status_pkey PRIMARY KEY (id);


--
-- Name: book_macro_section book_macro_section_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.book_macro_section
    ADD CONSTRAINT book_macro_section_pkey PRIMARY KEY (id);


--
-- Name: book_macro_section book_macro_section_section_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.book_macro_section
    ADD CONSTRAINT book_macro_section_section_key UNIQUE (section);


--
-- Name: booking booking_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_pkey PRIMARY KEY (id);


--
-- Name: booking booking_token_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT booking_token_key UNIQUE (token);


--
-- Name: boost_cinema_details boost_cinema_details_cinemaProviderPivotId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.boost_cinema_details
    ADD CONSTRAINT "boost_cinema_details_cinemaProviderPivotId_key" UNIQUE ("cinemaProviderPivotId");


--
-- Name: boost_cinema_details boost_cinema_details_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.boost_cinema_details
    ADD CONSTRAINT boost_cinema_details_pkey PRIMARY KEY (id);


--
-- Name: business_unit business_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit
    ADD CONSTRAINT business_unit_pkey PRIMARY KEY (id);


--
-- Name: business_unit business_unit_siret_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit
    ADD CONSTRAINT business_unit_siret_key UNIQUE (siret);


--
-- Name: business_unit_venue_link business_unit_venue_link_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit_venue_link
    ADD CONSTRAINT business_unit_venue_link_pkey PRIMARY KEY (id);


--
-- Name: business_unit_venue_link business_unit_venue_link_venueId_timespan_excl; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit_venue_link
    ADD CONSTRAINT "business_unit_venue_link_venueId_timespan_excl" EXCLUDE USING gist ("venueId" WITH =, timespan WITH &&);


--
-- Name: cashflow_batch cashflow_batch_cutoff_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_batch
    ADD CONSTRAINT cashflow_batch_cutoff_key UNIQUE (cutoff);


--
-- Name: cashflow_batch cashflow_batch_label_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_batch
    ADD CONSTRAINT cashflow_batch_label_key UNIQUE (label);


--
-- Name: cashflow_batch cashflow_batch_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_batch
    ADD CONSTRAINT cashflow_batch_pkey PRIMARY KEY (id);


--
-- Name: cashflow_log cashflow_log_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_log
    ADD CONSTRAINT cashflow_log_pkey PRIMARY KEY (id);


--
-- Name: cashflow cashflow_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT cashflow_pkey PRIMARY KEY (id);


--
-- Name: cashflow_pricing cashflow_pricing_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_pricing
    ADD CONSTRAINT cashflow_pricing_pkey PRIMARY KEY ("cashflowId", "pricingId");


--
-- Name: cashflow cashflow_transactionId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT "cashflow_transactionId_key" UNIQUE ("transactionId");


--
-- Name: cds_cinema_details cds_cinema_details_cinemaProviderPivotId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cds_cinema_details
    ADD CONSTRAINT "cds_cinema_details_cinemaProviderPivotId_key" UNIQUE ("cinemaProviderPivotId");


--
-- Name: cds_cinema_details cds_cinema_details_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cds_cinema_details
    ADD CONSTRAINT cds_cinema_details_pkey PRIMARY KEY (id);


--
-- Name: product check_iscgucompatible_is_not_null; Type: CHECK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE public.product
    ADD CONSTRAINT check_iscgucompatible_is_not_null CHECK (("isGcuCompatible" IS NOT NULL)) NOT VALID;


--
-- Name: cinema_provider_pivot cinema_provider_pivot_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot
    ADD CONSTRAINT cinema_provider_pivot_pkey PRIMARY KEY (id);


--
-- Name: cinema_provider_pivot cinema_provider_pivot_venueId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot
    ADD CONSTRAINT "cinema_provider_pivot_venueId_key" UNIQUE ("venueId");


--
-- Name: collective_booking collective_booking_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT collective_booking_pkey PRIMARY KEY (id);


--
-- Name: collective_offer_domain collective_offer_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_domain
    ADD CONSTRAINT collective_offer_domain_pkey PRIMARY KEY ("collectiveOfferId", "educationalDomainId");


--
-- Name: collective_offer collective_offer_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer
    ADD CONSTRAINT collective_offer_pkey PRIMARY KEY (id);


--
-- Name: collective_offer_template_domain collective_offer_template_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template_domain
    ADD CONSTRAINT collective_offer_template_domain_pkey PRIMARY KEY ("collectiveOfferTemplateId", "educationalDomainId");


--
-- Name: collective_offer_template collective_offer_template_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template
    ADD CONSTRAINT collective_offer_template_pkey PRIMARY KEY (id);


--
-- Name: collective_stock collective_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_stock
    ADD CONSTRAINT collective_stock_pkey PRIMARY KEY (id);


--
-- Name: criterion criterion_name_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.criterion
    ADD CONSTRAINT criterion_name_key UNIQUE (name);


--
-- Name: criterion criterion_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.criterion
    ADD CONSTRAINT criterion_pkey PRIMARY KEY (id);


--
-- Name: custom_reimbursement_rule custom_reimbursement_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.custom_reimbursement_rule
    ADD CONSTRAINT custom_reimbursement_rule_pkey PRIMARY KEY (id);


--
-- Name: deposit deposit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT deposit_pkey PRIMARY KEY (id);


--
-- Name: educational_deposit educational_deposit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_deposit
    ADD CONSTRAINT educational_deposit_pkey PRIMARY KEY (id);


--
-- Name: educational_domain educational_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain
    ADD CONSTRAINT educational_domain_pkey PRIMARY KEY (id);


--
-- Name: educational_domain_venue educational_domain_venue_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain_venue
    ADD CONSTRAINT educational_domain_venue_pkey PRIMARY KEY (id);


--
-- Name: educational_institution educational_institution_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_institution
    ADD CONSTRAINT educational_institution_pkey PRIMARY KEY (id);


--
-- Name: educational_redactor educational_redactor_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_redactor
    ADD CONSTRAINT educational_redactor_pkey PRIMARY KEY (id);


--
-- Name: educational_year educational_year_adageId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_year
    ADD CONSTRAINT "educational_year_adageId_key" UNIQUE ("adageId");


--
-- Name: educational_year educational_year_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_year
    ADD CONSTRAINT educational_year_pkey PRIMARY KEY (id);


--
-- Name: product event_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT "event_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: external_booking external_booking_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.external_booking
    ADD CONSTRAINT external_booking_pkey PRIMARY KEY (id);


--
-- Name: favorite favorite_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT favorite_pkey PRIMARY KEY (id);


--
-- Name: feature feature_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT feature_pkey PRIMARY KEY (id);


--
-- Name: individual_booking individual_booking_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.individual_booking
    ADD CONSTRAINT individual_booking_pkey PRIMARY KEY (id);


--
-- Name: invoice_line invoice_line_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_line
    ADD CONSTRAINT invoice_line_pkey PRIMARY KEY (id);


--
-- Name: invoice invoice_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_pkey PRIMARY KEY (id);


--
-- Name: invoice invoice_reference_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_reference_key UNIQUE (reference);


--
-- Name: invoice invoice_url_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT invoice_url_key UNIQUE (token);


--
-- Name: feature ix_feature_name; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT ix_feature_name UNIQUE (name);


--
-- Name: latest_dms_import latest_dms_import_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.latest_dms_import
    ADD CONSTRAINT latest_dms_import_pkey PRIMARY KEY (id);


--
-- Name: local_provider_event local_provider_event_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.local_provider_event
    ADD CONSTRAINT local_provider_event_pkey PRIMARY KEY (id);


--
-- Name: mediation mediation_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: mediation mediation_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT mediation_pkey PRIMARY KEY (id);


--
-- Name: offer_criterion offer_criterion_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT offer_criterion_pkey PRIMARY KEY (id);


--
-- Name: offer offer_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_pkey PRIMARY KEY (id);


--
-- Name: offer_report offer_report_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_report
    ADD CONSTRAINT offer_report_pkey PRIMARY KEY (id);


--
-- Name: offer_validation_config offer_validation_config_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_validation_config
    ADD CONSTRAINT offer_validation_config_pkey PRIMARY KEY (id);


--
-- Name: offerer offerer_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: offerer offerer_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT offerer_pkey PRIMARY KEY (id);


--
-- Name: offerer offerer_siren_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT offerer_siren_key UNIQUE (siren);


--
-- Name: offerer_tag_mapping offerer_tag_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag_mapping
    ADD CONSTRAINT offerer_tag_mapping_pkey PRIMARY KEY (id);


--
-- Name: offerer_tag offerer_tag_name_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag
    ADD CONSTRAINT offerer_tag_name_key UNIQUE (name);


--
-- Name: offerer_tag offerer_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag
    ADD CONSTRAINT offerer_tag_pkey PRIMARY KEY (id);


--
-- Name: offerer offerer_validationToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_validationToken_key" UNIQUE ("validationToken");


--
-- Name: orphan_dms_application orphan_dms_application_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.orphan_dms_application
    ADD CONSTRAINT orphan_dms_application_pkey PRIMARY KEY (id, application_id);


--
-- Name: payment_message payment_message_checksum_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_message
    ADD CONSTRAINT payment_message_checksum_key UNIQUE (checksum);


--
-- Name: payment_message payment_message_name_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_message
    ADD CONSTRAINT payment_message_name_key UNIQUE (name);


--
-- Name: payment_message payment_message_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_message
    ADD CONSTRAINT payment_message_pkey PRIMARY KEY (id);


--
-- Name: payment payment_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_pkey PRIMARY KEY (id);


--
-- Name: payment_status payment_status_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_status
    ADD CONSTRAINT payment_status_pkey PRIMARY KEY (id);


--
-- Name: permission permission_name_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_name_key UNIQUE (name);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);


--
-- Name: pricing_line pricing_line_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_line
    ADD CONSTRAINT pricing_line_pkey PRIMARY KEY (id);


--
-- Name: pricing_log pricing_log_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_log
    ADD CONSTRAINT pricing_log_pkey PRIMARY KEY (id);


--
-- Name: pricing pricing_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT pricing_pkey PRIMARY KEY (id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- Name: provider provider_localClass_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.provider
    ADD CONSTRAINT "provider_localClass_key" UNIQUE ("localClass");


--
-- Name: provider provider_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.provider
    ADD CONSTRAINT provider_pkey PRIMARY KEY (id);


--
-- Name: recredit recredit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.recredit
    ADD CONSTRAINT recredit_pkey PRIMARY KEY (id);


--
-- Name: reference_scheme reference_scheme_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.reference_scheme
    ADD CONSTRAINT reference_scheme_pkey PRIMARY KEY (id);


--
-- Name: role_backoffice_profile role_backoffice_profile_roleId_profileId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_backoffice_profile
    ADD CONSTRAINT "role_backoffice_profile_roleId_profileId_key" UNIQUE ("roleId", "profileId");


--
-- Name: role role_name_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_name_key UNIQUE (name);


--
-- Name: role_permission role_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT role_permission_pkey PRIMARY KEY (id);


--
-- Name: role_permission role_permission_roleId_permissionId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT "role_permission_roleId_permissionId_key" UNIQUE ("roleId", "permissionId");


--
-- Name: role role_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);


--
-- Name: stock stock_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: stock stock_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT stock_pkey PRIMARY KEY (id);


--
-- Name: token token_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.token
    ADD CONSTRAINT token_pkey PRIMARY KEY (id);


--
-- Name: transaction transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.transaction
    ADD CONSTRAINT transaction_pkey PRIMARY KEY (id);


--
-- Name: allocine_venue_provider_price_rule unique_allocine_venue_provider_price_rule; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider_price_rule
    ADD CONSTRAINT unique_allocine_venue_provider_price_rule UNIQUE ("allocineVenueProviderId", "priceRule");


--
-- Name: cashflow_pricing unique_cashflow_pricing_association; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_pricing
    ADD CONSTRAINT unique_cashflow_pricing_association UNIQUE ("cashflowId", "pricingId");


--
-- Name: activation_code unique_code_in_stock; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activation_code
    ADD CONSTRAINT unique_code_in_stock UNIQUE ("stockId", code);


--
-- Name: educational_domain_venue unique_educational_domain_venue; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain_venue
    ADD CONSTRAINT unique_educational_domain_venue UNIQUE ("educationalDomainId", "venueId");


--
-- Name: favorite unique_favorite; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT unique_favorite UNIQUE ("userId", "offerId");


--
-- Name: allocine_theater unique_internal_id; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_theater
    ADD CONSTRAINT unique_internal_id UNIQUE ("internalId");


--
-- Name: invoice_cashflow unique_invoice_cashflow_association; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_cashflow
    ADD CONSTRAINT unique_invoice_cashflow_association PRIMARY KEY ("invoiceId", "cashflowId");


--
-- Name: reference_scheme unique_name_year; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.reference_scheme
    ADD CONSTRAINT unique_name_year UNIQUE (name, year);


--
-- Name: offer_criterion unique_offer_criterion; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT unique_offer_criterion UNIQUE ("offerId", "criterionId");


--
-- Name: offer_report unique_offer_per_user; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_report
    ADD CONSTRAINT unique_offer_per_user UNIQUE ("userId", "offerId");


--
-- Name: offerer_tag_mapping unique_offerer_tag; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag_mapping
    ADD CONSTRAINT unique_offerer_tag UNIQUE ("offererId", "tagId");


--
-- Name: cinema_provider_pivot unique_pivot_venue_provider; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot
    ADD CONSTRAINT unique_pivot_venue_provider UNIQUE ("venueId", "providerId");


--
-- Name: reference_scheme unique_prefix_year; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.reference_scheme
    ADD CONSTRAINT unique_prefix_year UNIQUE (prefix, year);


--
-- Name: allocine_theater unique_siret; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_theater
    ADD CONSTRAINT unique_siret UNIQUE (siret);


--
-- Name: allocine_theater unique_theater_id; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_theater
    ADD CONSTRAINT unique_theater_id UNIQUE ("theaterId");


--
-- Name: deposit unique_type_per_user; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT unique_type_per_user UNIQUE ("userId", type);


--
-- Name: user_offerer unique_user_offerer; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT unique_user_offerer UNIQUE ("userId", "offererId");


--
-- Name: venue_criterion unique_venue_criterion; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_criterion
    ADD CONSTRAINT unique_venue_criterion UNIQUE ("venueId", "criterionId");


--
-- Name: venue_provider unique_venue_provider; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT unique_venue_provider UNIQUE ("venueId", "providerId", "venueIdAtOfferProvider");


--
-- Name: user_email_history user_email_history_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_email_history
    ADD CONSTRAINT user_email_history_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_idPieceNumber_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_idPieceNumber_key" UNIQUE ("idPieceNumber");


--
-- Name: user user_ineHash_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_ineHash_key" UNIQUE ("ineHash");


--
-- Name: user_offerer user_offerer_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT user_offerer_pkey PRIMARY KEY (id, "userId", "offererId");


--
-- Name: user_offerer user_offerer_validationToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT "user_offerer_validationToken_key" UNIQUE ("validationToken");


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user_session user_session_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_session
    ADD CONSTRAINT user_session_pkey PRIMARY KEY (id);


--
-- Name: user_session user_session_uuid_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_session
    ADD CONSTRAINT user_session_uuid_key UNIQUE (uuid);


--
-- Name: user_suspension user_suspension_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_suspension
    ADD CONSTRAINT user_suspension_pkey PRIMARY KEY (id);


--
-- Name: user user_validationToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_validationToken_key" UNIQUE ("validationToken");


--
-- Name: venue_contact venue_contact_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_contact
    ADD CONSTRAINT venue_contact_pkey PRIMARY KEY (id);


--
-- Name: venue_criterion venue_criterion_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_criterion
    ADD CONSTRAINT venue_criterion_pkey PRIMARY KEY (id);


--
-- Name: venue venue_dmsToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_dmsToken_key" UNIQUE ("dmsToken");


--
-- Name: venue_educational_status venue_educational_status_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_educational_status
    ADD CONSTRAINT venue_educational_status_pkey PRIMARY KEY (id);


--
-- Name: venue venue_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: venue_label venue_label_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_label
    ADD CONSTRAINT venue_label_pkey PRIMARY KEY (id);


--
-- Name: venue venue_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT venue_pkey PRIMARY KEY (id);


--
-- Name: venue_pricing_point_link venue_pricing_point_link_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_pricing_point_link
    ADD CONSTRAINT venue_pricing_point_link_pkey PRIMARY KEY (id);


--
-- Name: venue_pricing_point_link venue_pricing_point_link_venueId_timespan_excl; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_pricing_point_link
    ADD CONSTRAINT "venue_pricing_point_link_venueId_timespan_excl" EXCLUDE USING gist ("venueId" WITH =, timespan WITH &&);


--
-- Name: venue_provider venue_provider_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: venue_provider venue_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT venue_provider_pkey PRIMARY KEY (id);


--
-- Name: venue_reimbursement_point_link venue_reimbursement_point_link_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_reimbursement_point_link
    ADD CONSTRAINT venue_reimbursement_point_link_pkey PRIMARY KEY (id);


--
-- Name: venue_reimbursement_point_link venue_reimbursement_point_link_venueId_timespan_excl; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_reimbursement_point_link
    ADD CONSTRAINT "venue_reimbursement_point_link_venueId_timespan_excl" EXCLUDE USING gist ("venueId" WITH =, timespan WITH &&);


--
-- Name: venue venue_siret_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT venue_siret_key UNIQUE (siret);


--
-- Name: venue_type venue_type_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_type
    ADD CONSTRAINT venue_type_pkey PRIMARY KEY (id);


--
-- Name: idx_activity_changed_data; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_activity_changed_data ON public.activity USING btree (table_name, (((changed_data ->> 'id'::text))::integer));


--
-- Name: idx_activity_old_data; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_activity_old_data ON public.activity USING btree (table_name, (((old_data ->> 'id'::text))::integer));


--
-- Name: idx_offer_trgm_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_offer_trgm_name ON public.offer USING gin (name public.gin_trgm_ops);


--
-- Name: idx_offerer_fts_address; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_offerer_fts_address ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (address)::text));


--
-- Name: idx_offerer_fts_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_offerer_fts_name ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (name)::text));


--
-- Name: idx_offerer_fts_siret; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_offerer_fts_siret ON public.offerer USING gin (to_tsvector('public.french_unaccent'::regconfig, (siren)::text));


--
-- Name: idx_offerer_trgm_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_offerer_trgm_name ON public.offerer USING gin (name public.gin_trgm_ops);


--
-- Name: idx_uniq_booking_id; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX idx_uniq_booking_id ON public.pricing USING btree ("bookingId") WHERE (status <> 'cancelled'::text);


--
-- Name: idx_venue_fts_address; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_fts_address ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (address)::text));


--
-- Name: idx_venue_fts_city; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_fts_city ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (city)::text));


--
-- Name: idx_venue_fts_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_fts_name ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (name)::text));


--
-- Name: idx_venue_fts_publicName; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "idx_venue_fts_publicName" ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, ("publicName")::text));


--
-- Name: idx_venue_fts_siret; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_fts_siret ON public.venue USING gin (to_tsvector('public.french_unaccent'::regconfig, (siret)::text));


--
-- Name: idx_venue_trgm_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_trgm_name ON public.venue USING gin (name public.gin_trgm_ops);


--
-- Name: idx_venue_trgm_public_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_venue_trgm_public_name ON public.venue USING gin ("publicName" public.gin_trgm_ops);


--
-- Name: ix_action_history_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_action_history_offererId" ON public.action_history USING btree ("offererId");


--
-- Name: ix_action_history_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_action_history_userId" ON public.action_history USING btree ("userId");


--
-- Name: ix_action_history_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_action_history_venueId" ON public.action_history USING btree ("venueId");


--
-- Name: ix_activation_code_bookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_activation_code_bookingId" ON public.activation_code USING btree ("bookingId");


--
-- Name: ix_activation_code_stockId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_activation_code_stockId" ON public.activation_code USING btree ("stockId");


--
-- Name: ix_activity_transactionId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_activity_transactionId" ON public.activity USING btree (transaction_id);


--
-- Name: ix_allocine_venue_provider_price_rule_allocineVenueProviderId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_allocine_venue_provider_price_rule_allocineVenueProviderId" ON public.allocine_venue_provider_price_rule USING btree ("allocineVenueProviderId");


--
-- Name: ix_api_key_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_api_key_offererId" ON public.api_key USING btree ("offererId");


--
-- Name: ix_backoffice_user_profile_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_backoffice_user_profile_userId" ON public.backoffice_user_profile USING btree ("userId");


--
-- Name: ix_bank_information_applicationId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_bank_information_applicationId" ON public.bank_information USING btree ("applicationId");


--
-- Name: ix_bank_information_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_bank_information_offererId" ON public.bank_information USING btree ("offererId");


--
-- Name: ix_bank_information_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_bank_information_venueId" ON public.bank_information USING btree ("venueId");


--
-- Name: ix_beneficiary_fraud_check_thirdPartyId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_fraud_check_thirdPartyId" ON public.beneficiary_fraud_check USING btree ("thirdPartyId");


--
-- Name: ix_beneficiary_fraud_check_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_fraud_check_userId" ON public.beneficiary_fraud_check USING btree ("userId");


--
-- Name: ix_beneficiary_fraud_review_authorId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_fraud_review_authorId" ON public.beneficiary_fraud_review USING btree ("authorId");


--
-- Name: ix_beneficiary_fraud_review_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_fraud_review_userId" ON public.beneficiary_fraud_review USING btree ("userId");


--
-- Name: ix_beneficiary_import_beneficiaryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_import_beneficiaryId" ON public.beneficiary_import USING btree ("beneficiaryId");


--
-- Name: ix_beneficiary_import_status_beneficiaryImportId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_import_status_beneficiaryImportId" ON public.beneficiary_import_status USING btree ("beneficiaryImportId");


--
-- Name: ix_beneficiary_import_thirdPartyId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_import_thirdPartyId" ON public.beneficiary_import USING btree ("thirdPartyId");


--
-- Name: ix_booking_dateUsed; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_dateUsed" ON public.booking USING btree ("dateUsed");


--
-- Name: ix_booking_date_created; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_booking_date_created ON public.booking USING btree ("dateCreated");


--
-- Name: ix_booking_individualBookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_booking_individualBookingId" ON public.booking USING btree ("individualBookingId");


--
-- Name: ix_booking_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_offererId" ON public.booking USING btree ("offererId");


--
-- Name: ix_booking_reimbursementDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_reimbursementDate" ON public.booking USING btree ("reimbursementDate");


--
-- Name: ix_booking_status; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_booking_status ON public.booking USING btree (status);


--
-- Name: ix_booking_stockId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_stockId" ON public.booking USING btree ("stockId");


--
-- Name: ix_booking_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_userId" ON public.booking USING btree ("userId");


--
-- Name: ix_booking_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_venueId" ON public.booking USING btree ("venueId");


--
-- Name: ix_business_unit_bankAccountId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_business_unit_bankAccountId" ON public.business_unit USING btree ("bankAccountId");


--
-- Name: ix_business_unit_venue_link_businessUnitId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_business_unit_venue_link_businessUnitId" ON public.business_unit_venue_link USING btree ("businessUnitId");


--
-- Name: ix_business_unit_venue_link_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_business_unit_venue_link_venueId" ON public.business_unit_venue_link USING btree ("venueId");


--
-- Name: ix_cashflow_bankAccountId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_bankAccountId" ON public.cashflow USING btree ("bankAccountId");


--
-- Name: ix_cashflow_batchId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_batchId" ON public.cashflow USING btree ("batchId");


--
-- Name: ix_cashflow_businessUnitId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_businessUnitId" ON public.cashflow USING btree ("businessUnitId");


--
-- Name: ix_cashflow_log_cashflowId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_log_cashflowId" ON public.cashflow_log USING btree ("cashflowId");


--
-- Name: ix_cashflow_pricing_cashflowId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_pricing_cashflowId" ON public.cashflow_pricing USING btree ("cashflowId");


--
-- Name: ix_cashflow_pricing_pricingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_pricing_pricingId" ON public.cashflow_pricing USING btree ("pricingId");


--
-- Name: ix_cashflow_reimbursementPointId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_cashflow_reimbursementPointId" ON public.cashflow USING btree ("reimbursementPointId");


--
-- Name: ix_cashflow_status; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_cashflow_status ON public.cashflow USING btree (status);


--
-- Name: ix_collective_booking_collectiveStockId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_collectiveStockId" ON public.collective_booking USING btree ("collectiveStockId");


--
-- Name: ix_collective_booking_dateUsed; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_dateUsed" ON public.collective_booking USING btree ("dateUsed");


--
-- Name: ix_collective_booking_date_created; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_collective_booking_date_created ON public.collective_booking USING btree ("dateCreated");


--
-- Name: ix_collective_booking_educationalRedactorId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_educationalRedactorId" ON public.collective_booking USING btree ("educationalRedactorId");


--
-- Name: ix_collective_booking_educationalYear_and_institution; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_educationalYear_and_institution" ON public.collective_booking USING btree ("educationalYearId", "educationalInstitutionId");


--
-- Name: ix_collective_booking_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_offererId" ON public.collective_booking USING btree ("offererId");


--
-- Name: ix_collective_booking_status; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_collective_booking_status ON public.collective_booking USING btree (status);


--
-- Name: ix_collective_booking_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_booking_venueId" ON public.collective_booking USING btree ("venueId");


--
-- Name: ix_collective_offer_domain_collectiveOfferId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_domain_collectiveOfferId" ON public.collective_offer_domain USING btree ("collectiveOfferId");


--
-- Name: ix_collective_offer_domain_educationalDomainId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_domain_educationalDomainId" ON public.collective_offer_domain USING btree ("educationalDomainId");


--
-- Name: ix_collective_offer_institutionId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_institutionId" ON public.collective_offer USING btree ("institutionId");


--
-- Name: ix_collective_offer_lastValidationDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_lastValidationDate" ON public.collective_offer USING btree ("lastValidationDate");


--
-- Name: ix_collective_offer_subcategoryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_subcategoryId" ON public.collective_offer USING btree ("subcategoryId");


--
-- Name: ix_collective_offer_templateId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_templateId" ON public.collective_offer USING btree ("templateId");


--
-- Name: ix_collective_offer_template_domain_collectiveOfferTemplateId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_template_domain_collectiveOfferTemplateId" ON public.collective_offer_template_domain USING btree ("collectiveOfferTemplateId");


--
-- Name: ix_collective_offer_template_domain_educationalDomainId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_template_domain_educationalDomainId" ON public.collective_offer_template_domain USING btree ("educationalDomainId");


--
-- Name: ix_collective_offer_template_lastValidationDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_template_lastValidationDate" ON public.collective_offer_template USING btree ("lastValidationDate");


--
-- Name: ix_collective_offer_template_subcategoryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_template_subcategoryId" ON public.collective_offer_template USING btree ("subcategoryId");


--
-- Name: ix_collective_offer_template_validation; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_collective_offer_template_validation ON public.collective_offer_template USING btree (validation);


--
-- Name: ix_collective_offer_template_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_template_venueId" ON public.collective_offer_template USING btree ("venueId");


--
-- Name: ix_collective_offer_validation; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_collective_offer_validation ON public.collective_offer USING btree (validation);


--
-- Name: ix_collective_offer_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_offer_venueId" ON public.collective_offer USING btree ("venueId");


--
-- Name: ix_collective_stock_beginningDatetime; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_collective_stock_beginningDatetime" ON public.collective_stock USING btree ("beginningDatetime");


--
-- Name: ix_collective_stock_collectiveOfferId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_collective_stock_collectiveOfferId" ON public.collective_stock USING btree ("collectiveOfferId");


--
-- Name: ix_deposit_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_deposit_userId" ON public.deposit USING btree ("userId");


--
-- Name: ix_educational_deposit_educationalInstitutionId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_educational_deposit_educationalInstitutionId" ON public.educational_deposit USING btree ("educationalInstitutionId");


--
-- Name: ix_educational_deposit_educationalYearId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_educational_deposit_educationalYearId" ON public.educational_deposit USING btree ("educationalYearId");


--
-- Name: ix_educational_domain_venue_educationalDomainId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_educational_domain_venue_educationalDomainId" ON public.educational_domain_venue USING btree ("educationalDomainId");


--
-- Name: ix_educational_institution_institutionId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_educational_institution_institutionId" ON public.educational_institution USING btree ("institutionId");


--
-- Name: ix_educational_redactor_email; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX ix_educational_redactor_email ON public.educational_redactor USING btree (email);


--
-- Name: ix_external_booking_bookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_external_booking_bookingId" ON public.external_booking USING btree ("bookingId");


--
-- Name: ix_favorite_mediationId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_favorite_mediationId" ON public.favorite USING btree ("mediationId");


--
-- Name: ix_favorite_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_favorite_offerId" ON public.favorite USING btree ("offerId");


--
-- Name: ix_favorite_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_favorite_userId" ON public.favorite USING btree ("userId");


--
-- Name: ix_individual_booking_depositId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_individual_booking_depositId" ON public.individual_booking USING btree ("depositId");


--
-- Name: ix_individual_booking_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_individual_booking_userId" ON public.individual_booking USING btree ("userId");


--
-- Name: ix_invoice_businessUnitId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_invoice_businessUnitId" ON public.invoice USING btree ("businessUnitId");


--
-- Name: ix_invoice_cashflow_cashflowId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_invoice_cashflow_cashflowId" ON public.invoice_cashflow USING btree ("cashflowId");


--
-- Name: ix_invoice_cashflow_invoiceId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_invoice_cashflow_invoiceId" ON public.invoice_cashflow USING btree ("invoiceId");


--
-- Name: ix_invoice_line_invoiceId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_invoice_line_invoiceId" ON public.invoice_line USING btree ("invoiceId");


--
-- Name: ix_invoice_reimbursementPointId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_invoice_reimbursementPointId" ON public.invoice USING btree ("reimbursementPointId");


--
-- Name: ix_mediation_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_mediation_offerId" ON public.mediation USING btree ("offerId");


--
-- Name: ix_offer_criterion_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_criterion_offerId" ON public.offer_criterion USING btree ("offerId");


--
-- Name: ix_offer_lastValidationDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_lastValidationDate" ON public.offer USING btree ("lastValidationDate");


--
-- Name: ix_offer_productId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_productId" ON public.offer USING btree ("productId");


--
-- Name: ix_offer_report_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_report_offerId" ON public.offer_report USING btree ("offerId");


--
-- Name: ix_offer_report_reason; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_offer_report_reason ON public.offer_report USING btree (reason);


--
-- Name: ix_offer_report_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_report_userId" ON public.offer_report USING btree ("userId");


--
-- Name: ix_offer_subcategoryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_subcategoryId" ON public.offer USING btree ("subcategoryId");


--
-- Name: ix_offer_validation; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_offer_validation ON public.offer USING btree (validation);


--
-- Name: ix_offer_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_venueId" ON public.offer USING btree ("venueId");


--
-- Name: ix_offerer_tag_categoryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offerer_tag_categoryId" ON public.offerer_tag USING btree ("categoryId");


--
-- Name: ix_offerer_tag_mapping_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offerer_tag_mapping_offererId" ON public.offerer_tag_mapping USING btree ("offererId");


--
-- Name: ix_offerer_tag_mapping_tagId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offerer_tag_mapping_tagId" ON public.offerer_tag_mapping USING btree ("tagId");


--
-- Name: ix_orphan_dms_application_email; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_orphan_dms_application_email ON public.orphan_dms_application USING btree (email);


--
-- Name: ix_payment_batchDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_batchDate" ON public.payment USING btree ("batchDate");


--
-- Name: ix_payment_bookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_bookingId" ON public.payment USING btree ("bookingId");


--
-- Name: ix_payment_collectiveBookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_collectiveBookingId" ON public.payment USING btree ("collectiveBookingId");


--
-- Name: ix_payment_status_paymentId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_status_paymentId" ON public.payment_status USING btree ("paymentId");


--
-- Name: ix_pricing_bookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_bookingId" ON public.pricing USING btree ("bookingId");


--
-- Name: ix_pricing_businessUnitId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_businessUnitId" ON public.pricing USING btree ("businessUnitId");


--
-- Name: ix_pricing_collectiveBookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_collectiveBookingId" ON public.pricing USING btree ("collectiveBookingId");


--
-- Name: ix_pricing_customRuleId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_customRuleId" ON public.pricing USING btree ("customRuleId");


--
-- Name: ix_pricing_line_pricingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_line_pricingId" ON public.pricing_line USING btree ("pricingId");


--
-- Name: ix_pricing_log_pricingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_log_pricingId" ON public.pricing_log USING btree ("pricingId");


--
-- Name: ix_pricing_pricingPointId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_pricingPointId" ON public.pricing USING btree ("pricingPointId");


--
-- Name: ix_pricing_siret; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_pricing_siret ON public.pricing USING btree (siret);


--
-- Name: ix_pricing_status; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_pricing_status ON public.pricing USING btree (status);


--
-- Name: ix_pricing_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_pricing_venueId" ON public.pricing USING btree ("venueId");


--
-- Name: ix_product_subcategoryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_product_subcategoryId" ON public.product USING btree ("subcategoryId");


--
-- Name: ix_provider_name; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_provider_name ON public.provider USING btree (name);


--
-- Name: ix_stock_beginningDatetime; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_stock_beginningDatetime" ON public.stock USING btree ("beginningDatetime");


--
-- Name: ix_stock_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_stock_offerId" ON public.stock USING btree ("offerId");


--
-- Name: ix_token_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_token_userId" ON public.token USING btree ("userId");


--
-- Name: ix_token_value; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX ix_token_value ON public.token USING btree (value);


--
-- Name: ix_user_email_history_newDomainEmail; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_email_history_newDomainEmail" ON public.user_email_history USING btree ("newDomainEmail");


--
-- Name: ix_user_email_history_newUserEmail; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_email_history_newUserEmail" ON public.user_email_history USING btree ("newUserEmail");


--
-- Name: ix_user_email_history_oldDomainEmail; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_email_history_oldDomainEmail" ON public.user_email_history USING btree ("oldDomainEmail");


--
-- Name: ix_user_email_history_oldUserEmail; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_email_history_oldUserEmail" ON public.user_email_history USING btree ("oldUserEmail");


--
-- Name: ix_user_email_history_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_email_history_userId" ON public.user_email_history USING btree ("userId");


--
-- Name: ix_user_lower_email; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_user_lower_email ON public."user" USING btree (lower((email)::text));


--
-- Name: ix_user_offerer_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_offerer_offererId" ON public.user_offerer USING btree ("offererId");


--
-- Name: ix_user_phoneNumber; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_phoneNumber" ON public."user" USING btree ("phoneNumber");


--
-- Name: ix_user_suspension_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_suspension_userId" ON public.user_suspension USING btree ("userId");


--
-- Name: ix_user_validatedBirthDate; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_validatedBirthDate" ON public."user" USING btree ("validatedBirthDate");


--
-- Name: ix_venue_contact_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "ix_venue_contact_venueId" ON public.venue_contact USING btree ("venueId");


--
-- Name: ix_venue_criterion_criterionId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_criterion_criterionId" ON public.venue_criterion USING btree ("criterionId");


--
-- Name: ix_venue_criterion_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_criterion_venueId" ON public.venue_criterion USING btree ("venueId");


--
-- Name: ix_venue_managingOffererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_managingOffererId" ON public.venue USING btree ("managingOffererId");


--
-- Name: ix_venue_pricing_point_link_pricingPointId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_pricing_point_link_pricingPointId" ON public.venue_pricing_point_link USING btree ("pricingPointId");


--
-- Name: ix_venue_pricing_point_link_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_pricing_point_link_venueId" ON public.venue_pricing_point_link USING btree ("venueId");


--
-- Name: ix_venue_provider_providerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_provider_providerId" ON public.venue_provider USING btree ("providerId");


--
-- Name: ix_venue_reimbursement_point_link_reimbursementPointId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_reimbursement_point_link_reimbursementPointId" ON public.venue_reimbursement_point_link USING btree ("reimbursementPointId");


--
-- Name: ix_venue_reimbursement_point_link_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_reimbursement_point_link_venueId" ON public.venue_reimbursement_point_link USING btree ("venueId");


--
-- Name: offer_isbn_idx; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX offer_isbn_idx ON public.offer USING btree ((("jsonData" ->> 'isbn'::text)));


--
-- Name: product_isbn_idx; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX product_isbn_idx ON public.product USING btree ((("jsonData" ->> 'isbn'::text)));


--
-- Name: venueId_idAtProvider_index; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX "venueId_idAtProvider_index" ON public.offer USING btree ("venueId", "idAtProvider");


--
-- Name: booking booking_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE OF quantity, amount, status, "userId" ON public.booking NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.check_booking();


--
-- Name: stock stock_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE ON public.stock NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.check_stock();


--
-- Name: booking stock_update_cancellation_date; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER stock_update_cancellation_date BEFORE INSERT OR UPDATE OF status ON public.booking FOR EACH ROW EXECUTE FUNCTION public.save_cancellation_date();


--
-- Name: stock stock_update_modification_date; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER stock_update_modification_date BEFORE UPDATE ON public.stock FOR EACH ROW EXECUTE FUNCTION public.save_stock_modification_date();


--
-- Name: action_history action_history_authorUserId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history
    ADD CONSTRAINT "action_history_authorUserId_fkey" FOREIGN KEY ("authorUserId") REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: action_history action_history_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history
    ADD CONSTRAINT "action_history_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id) ON DELETE CASCADE;


--
-- Name: action_history action_history_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history
    ADD CONSTRAINT "action_history_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: action_history action_history_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.action_history
    ADD CONSTRAINT "action_history_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id) ON DELETE CASCADE;


--
-- Name: activation_code activation_code_bookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activation_code
    ADD CONSTRAINT "activation_code_bookingId_fkey" FOREIGN KEY ("bookingId") REFERENCES public.booking(id);


--
-- Name: activation_code activation_code_stockId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activation_code
    ADD CONSTRAINT "activation_code_stockId_fkey" FOREIGN KEY ("stockId") REFERENCES public.stock(id);


--
-- Name: allocine_pivot allocine_pivot_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT "allocine_pivot_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: allocine_venue_provider allocine_venue_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider
    ADD CONSTRAINT allocine_venue_provider_id_fkey FOREIGN KEY (id) REFERENCES public.venue_provider(id);


--
-- Name: allocine_venue_provider_price_rule allocine_venue_provider_price_rule_allocineVenueProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider_price_rule
    ADD CONSTRAINT "allocine_venue_provider_price_rule_allocineVenueProviderId_fkey" FOREIGN KEY ("allocineVenueProviderId") REFERENCES public.allocine_venue_provider(id);


--
-- Name: api_key api_key_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.api_key
    ADD CONSTRAINT "api_key_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: backoffice_user_profile backoffice_user_profile_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.backoffice_user_profile
    ADD CONSTRAINT "backoffice_user_profile_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: bank_information bank_information_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information
    ADD CONSTRAINT "bank_information_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: bank_information bank_information_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information
    ADD CONSTRAINT "bank_information_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: beneficiary_fraud_check beneficiary_fraud_check_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_check
    ADD CONSTRAINT "beneficiary_fraud_check_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: beneficiary_fraud_review beneficiary_fraud_review_authorId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_review
    ADD CONSTRAINT "beneficiary_fraud_review_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES public."user"(id);


--
-- Name: beneficiary_fraud_review beneficiary_fraud_review_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_fraud_review
    ADD CONSTRAINT "beneficiary_fraud_review_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: beneficiary_import beneficiary_import_beneficiaryId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import
    ADD CONSTRAINT "beneficiary_import_beneficiaryId_fkey" FOREIGN KEY ("beneficiaryId") REFERENCES public."user"(id);


--
-- Name: beneficiary_import_status beneficiary_import_status_authorId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import_status
    ADD CONSTRAINT "beneficiary_import_status_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES public."user"(id);


--
-- Name: beneficiary_import_status beneficiary_import_status_beneficiaryImportId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import_status
    ADD CONSTRAINT "beneficiary_import_status_beneficiaryImportId_fkey" FOREIGN KEY ("beneficiaryImportId") REFERENCES public.beneficiary_import(id);


--
-- Name: booking booking_individualBookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_individualBookingId_fkey" FOREIGN KEY ("individualBookingId") REFERENCES public.individual_booking(id);


--
-- Name: booking booking_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: booking booking_stockId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_stockId_fkey" FOREIGN KEY ("stockId") REFERENCES public.stock(id);


--
-- Name: booking booking_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: booking booking_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking
    ADD CONSTRAINT "booking_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: boost_cinema_details boost_cinema_details_cinemaProviderPivotId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.boost_cinema_details
    ADD CONSTRAINT "boost_cinema_details_cinemaProviderPivotId_fkey" FOREIGN KEY ("cinemaProviderPivotId") REFERENCES public.cinema_provider_pivot(id);


--
-- Name: business_unit business_unit_bankAccountId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit
    ADD CONSTRAINT "business_unit_bankAccountId_fkey" FOREIGN KEY ("bankAccountId") REFERENCES public.bank_information(id);


--
-- Name: business_unit_venue_link business_unit_venue_link_businessUnitId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit_venue_link
    ADD CONSTRAINT "business_unit_venue_link_businessUnitId_fkey" FOREIGN KEY ("businessUnitId") REFERENCES public.business_unit(id);


--
-- Name: business_unit_venue_link business_unit_venue_link_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.business_unit_venue_link
    ADD CONSTRAINT "business_unit_venue_link_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: cashflow cashflow_bankAccountId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT "cashflow_bankAccountId_fkey" FOREIGN KEY ("bankAccountId") REFERENCES public.bank_information(id);


--
-- Name: cashflow cashflow_batchId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT "cashflow_batchId_fkey" FOREIGN KEY ("batchId") REFERENCES public.cashflow_batch(id);


--
-- Name: cashflow cashflow_businessUnitId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT "cashflow_businessUnitId_fkey" FOREIGN KEY ("businessUnitId") REFERENCES public.business_unit(id);


--
-- Name: cashflow_log cashflow_log_cashflowId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_log
    ADD CONSTRAINT "cashflow_log_cashflowId_fkey" FOREIGN KEY ("cashflowId") REFERENCES public.cashflow(id);


--
-- Name: cashflow_pricing cashflow_pricing_cashflowId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_pricing
    ADD CONSTRAINT "cashflow_pricing_cashflowId_fkey" FOREIGN KEY ("cashflowId") REFERENCES public.cashflow(id);


--
-- Name: cashflow_pricing cashflow_pricing_pricingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow_pricing
    ADD CONSTRAINT "cashflow_pricing_pricingId_fkey" FOREIGN KEY ("pricingId") REFERENCES public.pricing(id);


--
-- Name: cashflow cashflow_reimbursementPointId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cashflow
    ADD CONSTRAINT "cashflow_reimbursementPointId_fkey" FOREIGN KEY ("reimbursementPointId") REFERENCES public.venue(id);


--
-- Name: cds_cinema_details cds_cinema_details_cinemaProviderPivotId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cds_cinema_details
    ADD CONSTRAINT "cds_cinema_details_cinemaProviderPivotId_fkey" FOREIGN KEY ("cinemaProviderPivotId") REFERENCES public.cinema_provider_pivot(id);


--
-- Name: cinema_provider_pivot cinema_provider_pivot_providerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot
    ADD CONSTRAINT "cinema_provider_pivot_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES public.provider(id);


--
-- Name: cinema_provider_pivot cinema_provider_pivot_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.cinema_provider_pivot
    ADD CONSTRAINT "cinema_provider_pivot_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: collective_booking collective_booking_collectiveStockId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_collectiveStockId_fkey" FOREIGN KEY ("collectiveStockId") REFERENCES public.collective_stock(id);


--
-- Name: collective_booking collective_booking_educationalInstitutionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_educationalInstitutionId_fkey" FOREIGN KEY ("educationalInstitutionId") REFERENCES public.educational_institution(id);


--
-- Name: collective_booking collective_booking_educationalRedactorId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_educationalRedactorId_fkey" FOREIGN KEY ("educationalRedactorId") REFERENCES public.educational_redactor(id);


--
-- Name: collective_booking collective_booking_educationalYearId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_educationalYearId_fkey" FOREIGN KEY ("educationalYearId") REFERENCES public.educational_year("adageId");


--
-- Name: collective_booking collective_booking_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: collective_booking collective_booking_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_booking
    ADD CONSTRAINT "collective_booking_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: collective_offer_domain collective_offer_domain_collectiveOfferId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_domain
    ADD CONSTRAINT "collective_offer_domain_collectiveOfferId_fkey" FOREIGN KEY ("collectiveOfferId") REFERENCES public.collective_offer(id) ON DELETE CASCADE;


--
-- Name: collective_offer_domain collective_offer_domain_educationalDomainId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_domain
    ADD CONSTRAINT "collective_offer_domain_educationalDomainId_fkey" FOREIGN KEY ("educationalDomainId") REFERENCES public.educational_domain(id) ON DELETE CASCADE;


--
-- Name: collective_offer collective_offer_educational_institution_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer
    ADD CONSTRAINT collective_offer_educational_institution_fkey FOREIGN KEY ("institutionId") REFERENCES public.educational_institution(id);


--
-- Name: collective_offer_template_domain collective_offer_template_domain_collectiveOfferTemplateId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template_domain
    ADD CONSTRAINT "collective_offer_template_domain_collectiveOfferTemplateId_fkey" FOREIGN KEY ("collectiveOfferTemplateId") REFERENCES public.collective_offer_template(id) ON DELETE CASCADE;


--
-- Name: collective_offer_template_domain collective_offer_template_domain_educationalDomainId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template_domain
    ADD CONSTRAINT "collective_offer_template_domain_educationalDomainId_fkey" FOREIGN KEY ("educationalDomainId") REFERENCES public.educational_domain(id) ON DELETE CASCADE;


--
-- Name: collective_offer collective_offer_template_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer
    ADD CONSTRAINT collective_offer_template_fkey FOREIGN KEY ("templateId") REFERENCES public.collective_offer_template(id);


--
-- Name: collective_offer_template collective_offer_template_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer_template
    ADD CONSTRAINT "collective_offer_template_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: collective_offer collective_offer_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_offer
    ADD CONSTRAINT "collective_offer_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: collective_stock collective_stock_collectiveOfferId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.collective_stock
    ADD CONSTRAINT "collective_stock_collectiveOfferId_fkey" FOREIGN KEY ("collectiveOfferId") REFERENCES public.collective_offer(id);


--
-- Name: custom_reimbursement_rule custom_reimbursement_rule_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.custom_reimbursement_rule
    ADD CONSTRAINT "custom_reimbursement_rule_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


--
-- Name: custom_reimbursement_rule custom_reimbursement_rule_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.custom_reimbursement_rule
    ADD CONSTRAINT "custom_reimbursement_rule_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: deposit deposit_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT "deposit_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: educational_deposit educational_deposit_educationalInstitutionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_deposit
    ADD CONSTRAINT "educational_deposit_educationalInstitutionId_fkey" FOREIGN KEY ("educationalInstitutionId") REFERENCES public.educational_institution(id);


--
-- Name: educational_deposit educational_deposit_educationalYearId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_deposit
    ADD CONSTRAINT "educational_deposit_educationalYearId_fkey" FOREIGN KEY ("educationalYearId") REFERENCES public.educational_year("adageId");


--
-- Name: educational_domain_venue educational_domain_venue_educationalDomainId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain_venue
    ADD CONSTRAINT "educational_domain_venue_educationalDomainId_fkey" FOREIGN KEY ("educationalDomainId") REFERENCES public.educational_domain(id) ON DELETE CASCADE;


--
-- Name: educational_domain_venue educational_domain_venue_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.educational_domain_venue
    ADD CONSTRAINT "educational_domain_venue_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id) ON DELETE CASCADE;


--
-- Name: product event_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT "event_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: external_booking external_booking_bookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.external_booking
    ADD CONSTRAINT "external_booking_bookingId_fkey" FOREIGN KEY ("bookingId") REFERENCES public.booking(id);


--
-- Name: favorite favorite_mediationId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT "favorite_mediationId_fkey" FOREIGN KEY ("mediationId") REFERENCES public.mediation(id);


--
-- Name: favorite favorite_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT "favorite_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


--
-- Name: favorite favorite_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT "favorite_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: individual_booking individual_booking_depositId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.individual_booking
    ADD CONSTRAINT "individual_booking_depositId_fkey" FOREIGN KEY ("depositId") REFERENCES public.deposit(id);


--
-- Name: individual_booking individual_booking_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.individual_booking
    ADD CONSTRAINT "individual_booking_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: invoice invoice_businessUnitId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT "invoice_businessUnitId_fkey" FOREIGN KEY ("businessUnitId") REFERENCES public.business_unit(id);


--
-- Name: invoice_cashflow invoice_cashflow_cashflowId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_cashflow
    ADD CONSTRAINT "invoice_cashflow_cashflowId_fkey" FOREIGN KEY ("cashflowId") REFERENCES public.cashflow(id);


--
-- Name: invoice_cashflow invoice_cashflow_invoiceId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_cashflow
    ADD CONSTRAINT "invoice_cashflow_invoiceId_fkey" FOREIGN KEY ("invoiceId") REFERENCES public.invoice(id);


--
-- Name: invoice_line invoice_line_invoiceId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice_line
    ADD CONSTRAINT "invoice_line_invoiceId_fkey" FOREIGN KEY ("invoiceId") REFERENCES public.invoice(id);


--
-- Name: invoice invoice_reimbursementPointId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.invoice
    ADD CONSTRAINT "invoice_reimbursementPointId_fkey" FOREIGN KEY ("reimbursementPointId") REFERENCES public.venue(id);


--
-- Name: local_provider_event local_provider_event_providerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.local_provider_event
    ADD CONSTRAINT "local_provider_event_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES public.provider(id);


--
-- Name: mediation mediation_authorId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES public."user"(id);


--
-- Name: mediation mediation_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: mediation mediation_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.mediation
    ADD CONSTRAINT "mediation_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


--
-- Name: offer offer_authorId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES public."user"(id);


--
-- Name: offer_criterion offer_criterion_criterionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT "offer_criterion_criterionId_fkey" FOREIGN KEY ("criterionId") REFERENCES public.criterion(id) ON DELETE CASCADE;


--
-- Name: offer_criterion offer_criterion_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT "offer_criterion_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id) ON DELETE CASCADE;


--
-- Name: offer offer_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: offer offer_productId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_productId_fkey" FOREIGN KEY ("productId") REFERENCES public.product(id);


--
-- Name: offer_report offer_report_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_report
    ADD CONSTRAINT "offer_report_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id) ON DELETE CASCADE;


--
-- Name: offer_report offer_report_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_report
    ADD CONSTRAINT "offer_report_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: offer_validation_config offer_validation_config_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_validation_config
    ADD CONSTRAINT "offer_validation_config_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: offer offer_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: offerer offerer_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: offerer_tag_mapping offerer_tag_mapping_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag_mapping
    ADD CONSTRAINT "offerer_tag_mapping_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id) ON DELETE CASCADE;


--
-- Name: offerer_tag_mapping offerer_tag_mapping_tagId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer_tag_mapping
    ADD CONSTRAINT "offerer_tag_mapping_tagId_fkey" FOREIGN KEY ("tagId") REFERENCES public.offerer_tag(id) ON DELETE CASCADE;


--
-- Name: payment payment_bookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_bookingId_fkey" FOREIGN KEY ("bookingId") REFERENCES public.booking(id);


--
-- Name: payment payment_collective_booking_fk; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT payment_collective_booking_fk FOREIGN KEY ("collectiveBookingId") REFERENCES public.collective_booking(id);


--
-- Name: payment payment_customReimbursementRuleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_customReimbursementRuleId_fkey" FOREIGN KEY ("customReimbursementRuleId") REFERENCES public.custom_reimbursement_rule(id);


--
-- Name: payment payment_paymentMessageId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_paymentMessageId_fkey" FOREIGN KEY ("paymentMessageId") REFERENCES public.payment_message(id);


--
-- Name: payment_status payment_status_paymentId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment_status
    ADD CONSTRAINT "payment_status_paymentId_fkey" FOREIGN KEY ("paymentId") REFERENCES public.payment(id);


--
-- Name: pricing pricing_bookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT "pricing_bookingId_fkey" FOREIGN KEY ("bookingId") REFERENCES public.booking(id);


--
-- Name: pricing pricing_businessUnitId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT "pricing_businessUnitId_fkey" FOREIGN KEY ("businessUnitId") REFERENCES public.business_unit(id);


--
-- Name: pricing pricing_collective_booking_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT pricing_collective_booking_fkey FOREIGN KEY ("collectiveBookingId") REFERENCES public.collective_booking(id);


--
-- Name: pricing pricing_customRuleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT "pricing_customRuleId_fkey" FOREIGN KEY ("customRuleId") REFERENCES public.custom_reimbursement_rule(id);


--
-- Name: pricing_line pricing_line_pricingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_line
    ADD CONSTRAINT "pricing_line_pricingId_fkey" FOREIGN KEY ("pricingId") REFERENCES public.pricing(id);


--
-- Name: pricing_log pricing_log_pricingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing_log
    ADD CONSTRAINT "pricing_log_pricingId_fkey" FOREIGN KEY ("pricingId") REFERENCES public.pricing(id);


--
-- Name: pricing pricing_pricingPointId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT "pricing_pricingPointId_fkey" FOREIGN KEY ("pricingPointId") REFERENCES public.venue(id);


--
-- Name: pricing pricing_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.pricing
    ADD CONSTRAINT "pricing_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: product product_owning_offerer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_owning_offerer_id_fkey FOREIGN KEY ("owningOffererId") REFERENCES public.offerer(id);


--
-- Name: recredit recredit_depositId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.recredit
    ADD CONSTRAINT "recredit_depositId_fkey" FOREIGN KEY ("depositId") REFERENCES public.deposit(id);


--
-- Name: role_backoffice_profile role_backoffice_profile_profileId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_backoffice_profile
    ADD CONSTRAINT "role_backoffice_profile_profileId_fkey" FOREIGN KEY ("profileId") REFERENCES public.backoffice_user_profile(id) ON DELETE CASCADE;


--
-- Name: role_backoffice_profile role_backoffice_profile_roleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_backoffice_profile
    ADD CONSTRAINT "role_backoffice_profile_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: role_permission role_permission_permissionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT "role_permission_permissionId_fkey" FOREIGN KEY ("permissionId") REFERENCES public.permission(id) ON DELETE CASCADE;


--
-- Name: role_permission role_permission_roleId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.role_permission
    ADD CONSTRAINT "role_permission_roleId_fkey" FOREIGN KEY ("roleId") REFERENCES public.role(id) ON DELETE CASCADE;


--
-- Name: stock stock_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: stock stock_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.stock
    ADD CONSTRAINT "stock_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


--
-- Name: token token_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.token
    ADD CONSTRAINT "token_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: user_email_history user_email_history_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_email_history
    ADD CONSTRAINT "user_email_history_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: user_offerer user_offerer_offererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT "user_offerer_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES public.offerer(id);


--
-- Name: user_offerer user_offerer_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT "user_offerer_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: user_suspension user_suspension_actorUserId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_suspension
    ADD CONSTRAINT "user_suspension_actorUserId_fkey" FOREIGN KEY ("actorUserId") REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: user_suspension user_suspension_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_suspension
    ADD CONSTRAINT "user_suspension_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: venue venue_businessUnitId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_businessUnitId_fkey" FOREIGN KEY ("businessUnitId") REFERENCES public.business_unit(id);


--
-- Name: venue_contact venue_contact_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_contact
    ADD CONSTRAINT "venue_contact_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id) ON DELETE CASCADE;


--
-- Name: venue_criterion venue_criterion_criterionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_criterion
    ADD CONSTRAINT "venue_criterion_criterionId_fkey" FOREIGN KEY ("criterionId") REFERENCES public.criterion(id) ON DELETE CASCADE;


--
-- Name: venue_criterion venue_criterion_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_criterion
    ADD CONSTRAINT "venue_criterion_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id) ON DELETE CASCADE;


--
-- Name: venue venue_educational_status_venue_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT venue_educational_status_venue_fkey FOREIGN KEY ("venueEducationalStatusId") REFERENCES public.venue_educational_status(id);


--
-- Name: venue venue_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: venue venue_managingOffererId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_managingOffererId_fkey" FOREIGN KEY ("managingOffererId") REFERENCES public.offerer(id);


--
-- Name: venue_pricing_point_link venue_pricing_point_link_pricingPointId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_pricing_point_link
    ADD CONSTRAINT "venue_pricing_point_link_pricingPointId_fkey" FOREIGN KEY ("pricingPointId") REFERENCES public.venue(id);


--
-- Name: venue_pricing_point_link venue_pricing_point_link_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_pricing_point_link
    ADD CONSTRAINT "venue_pricing_point_link_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: venue_provider venue_provider_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


--
-- Name: venue_provider venue_provider_providerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES public.provider(id);


--
-- Name: venue_provider venue_provider_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT "venue_provider_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: venue_reimbursement_point_link venue_reimbursement_point_link_reimbursementPointId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_reimbursement_point_link
    ADD CONSTRAINT "venue_reimbursement_point_link_reimbursementPointId_fkey" FOREIGN KEY ("reimbursementPointId") REFERENCES public.venue(id);


--
-- Name: venue_reimbursement_point_link venue_reimbursement_point_link_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_reimbursement_point_link
    ADD CONSTRAINT "venue_reimbursement_point_link_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


--
-- Name: venue venue_venueLabelId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_venueLabelId_fkey" FOREIGN KEY ("venueLabelId") REFERENCES public.venue_label(id);


--
-- Name: venue venue_venueTypeId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT "venue_venueTypeId_fkey" FOREIGN KEY ("venueTypeId") REFERENCES public.venue_type(id);


--
-- PostgreSQL database dump complete
--

