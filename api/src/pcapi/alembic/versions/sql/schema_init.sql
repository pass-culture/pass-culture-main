--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3 (Debian 12.3-1.pgdg100+1)
-- Dumped by pg_dump version 12.3 (Debian 12.3-1.pgdg100+1)

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

SET search_path = public, pg_catalog;

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: pass_culture
--


--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: pass_culture
--


--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: pass_culture
--


--
-- Name: SCHEMA topology; Type: COMMENT; Schema: -; Owner: pass_culture
--
CREATE SCHEMA IF NOT EXISTS tiger;
CREATE SCHEMA IF NOT EXISTS topology;
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
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: cancellation_reason; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.cancellation_reason AS ENUM (
    'OFFERER',
    'BENEFICIARY',
    'EXPIRED'
);



--
-- Name: emailstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.emailstatus AS ENUM (
    'SENT',
    'ERROR'
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
    'WEBAPP_SIGNUP',
    'DEGRESSIVE_REIMBURSEMENT_RATE',
    'QR_CODE',
    'FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE',
    'SEARCH_ALGOLIA',
    'SEARCH_LEGACY',
    'BENEFICIARIES_IMPORT',
    'SYNCHRONIZE_ALGOLIA',
    'SYNCHRONIZE_ALLOCINE',
    'SYNCHRONIZE_BANK_INFORMATION',
    'SYNCHRONIZE_LIBRAIRES',
    'SYNCHRONIZE_TITELIVE',
    'SYNCHRONIZE_TITELIVE_PRODUCTS',
    'SYNCHRONIZE_TITELIVE_PRODUCTS_DESCRIPTION',
    'SYNCHRONIZE_TITELIVE_PRODUCTS_THUMBS',
    'UPDATE_DISCOVERY_VIEW',
    'UPDATE_BOOKING_USED',
    'RECOMMENDATIONS_WITH_DISCOVERY_VIEW',
    'RECOMMENDATIONS_WITH_DIGITAL_FIRST',
    'RECOMMENDATIONS_WITH_GEOLOCATION',
    'NEW_RIBS_UPLOAD',
    'SAVE_SEEN_OFFERS',
    'BOOKINGS_V2',
    'API_SIRENE_AVAILABLE',
    'CLEAN_DISCOVERY_VIEW',
    'WEBAPP_HOMEPAGE',
    'WEBAPP_PROFILE_PAGE',
    'APPLY_BOOKING_LIMITS_V2'
);



--
-- Name: importstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.importstatus AS ENUM (
    'DUPLICATE',
    'CREATED',
    'ERROR',
    'REJECTED',
    'RETRY'
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
-- Name: pricerule; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.pricerule AS ENUM (
    'default'
);



--
-- Name: rightstype; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.rightstype AS ENUM (
    'admin',
    'editor'
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
-- Name: transactionstatus; Type: TYPE; Schema: public; Owner: pass_culture
--

CREATE TYPE public.transactionstatus AS ENUM (
    'PENDING',
    'NOT_PROCESSABLE',
    'SENT',
    'ERROR',
    'RETRY',
    'BANNED'
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
    BEGIN
      IF EXISTS (SELECT "quantity" FROM stock WHERE id=NEW."stockId" AND "quantity" IS NOT NULL)
         AND (
             (SELECT "quantity" FROM stock WHERE id=NEW."stockId")
              <
              (SELECT SUM(quantity) FROM booking WHERE "stockId"=NEW."stockId" AND NOT "isCancelled")
              )
         THEN RAISE EXCEPTION 'tooManyBookings'
                    USING HINT = 'Number of bookings cannot exceed "stock.quantity"';
      END IF;

      IF (
        (
          -- If this is a new booking, we probably want to check the wallet.
          OLD IS NULL
          -- If we're updating an existing booking...
          OR (
            -- Check the wallet if we are changing the quantity or the amount
            -- The backend should never do that, but let's be defensive.
            (NEW."quantity" != OLD."quantity" OR NEW."amount" != OLD."amount")
            -- If amount and quantity are unchanged, we want to check the wallet
            -- only if we are UNcancelling a booking (which the backend should never
            -- do, but let's be defensive). Users with no credits left should
            -- be able to cancel their booking. Also, their booking can
            -- be marked as used or not used.
            OR (NEW."isCancelled" != OLD."isCancelled" AND NOT NEW."isCancelled")
          )
        )
        -- Allow to book free offers even with no credit left (or expired deposits)
        AND (NEW."amount" != 0)
        AND (get_wallet_balance(NEW."userId", false) < 0)
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
              AND NOT booking."isCancelled"
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
-- Name: create_activity(); Type: FUNCTION; Schema: public; Owner: pass_culture
--

CREATE FUNCTION public.create_activity() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog', 'public'
    AS $$
DECLARE
    audit_row public.activity;
    excluded_cols text[] = ARRAY[]::text[];
    _transaction_id BIGINT;
BEGIN
    _transaction_id := (
        SELECT id
        FROM public.transaction
        WHERE
            native_transaction_id = txid_current() AND
            issued_at >= (NOW() - INTERVAL '1 day')
        ORDER BY issued_at DESC
        LIMIT 1
    );

    IF TG_ARGV[0] IS NOT NULL THEN
        excluded_cols = TG_ARGV[0]::text[];
    END IF;

    IF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.activity
        SELECT
            nextval('public.activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            old_data - excluded_cols AS old_data,
            new_data - old_data - excluded_cols AS changed_data,
            _transaction_id AS transaction_id
        FROM (
            SELECT *
            FROM (
                SELECT
                    row_to_json(old_table.*)::jsonb AS old_data,
                    row_number() OVER ()
                FROM old_table
            ) AS old_table
            JOIN (
                SELECT
                    row_to_json(new_table.*)::jsonb AS new_data,
                    row_number() OVER ()
                FROM new_table
            ) AS new_table
            USING(row_number)
        ) as sub
        WHERE new_data - old_data - excluded_cols != '{}'::jsonb;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO public.activity
        SELECT
            nextval('public.activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            '{}'::jsonb AS old_data,
            row_to_json(new_table.*)::jsonb - excluded_cols,
            _transaction_id AS transaction_id
        FROM new_table;
    ELSEIF TG_OP = 'DELETE' THEN
        INSERT INTO public.activity
        SELECT
            nextval('public.activity_id_seq') as id,
            TG_TABLE_SCHEMA::text AS schema_name,
            TG_TABLE_NAME::text AS table_name,
            TG_RELID AS relid,
            statement_timestamp() AT TIME ZONE 'UTC' AS issued_at,
            txid_current() AS native_transaction_id,
            LOWER(TG_OP) AS verb,
            row_to_json(old_table.*)::jsonb - excluded_cols AS old_data,
            '{}'::jsonb AS changed_data,
            _transaction_id AS transaction_id
        FROM old_table;
    END IF;
    RETURN NULL;
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
        sum_deposits NUMERIC ;
        sum_bookings NUMERIC ;
    BEGIN
        SELECT COALESCE(SUM(amount), 0)
        INTO sum_deposits
        FROM deposit
        WHERE "userId"=user_id
        AND ("expirationDate" > now() OR "expirationDate" IS NULL);

        CASE
            only_used_bookings
        WHEN true THEN
            SELECT COALESCE(SUM(amount * quantity), 0)
            INTO sum_bookings
            FROM booking
            WHERE "userId"=user_id AND NOT "isCancelled" AND "isUsed" = true;
        WHEN false THEN
            SELECT COALESCE(SUM(amount * quantity), 0)
            INTO sum_bookings
            FROM booking
            WHERE "userId"=user_id AND NOT "isCancelled";
        END CASE;

        RETURN (sum_deposits - sum_bookings);
    END; $$;



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
                    IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL THEN
                        NEW."cancellationDate" = NOW();
                    ELSIF NEW."isCancelled" IS FALSE THEN
                        NEW."cancellationDate" = null;
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
    siret character varying(14) NOT NULL,
    "theaterId" character varying(20) NOT NULL
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
-- Name: allocine_venue_provider; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.allocine_venue_provider (
    id bigint NOT NULL,
    "isDuo" boolean DEFAULT true NOT NULL,
    quantity integer
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
    value character varying(64) NOT NULL
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
-- Name: bank_information; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.bank_information (
    id bigint NOT NULL,
    "offererId" bigint,
    "venueId" bigint,
    iban character varying(27),
    bic character varying(11),
    "applicationId" integer NOT NULL,
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
-- Name: beneficiary_import; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.beneficiary_import (
    id bigint NOT NULL,
    "beneficiaryId" bigint,
    "applicationId" bigint NOT NULL,
    "sourceId" integer,
    source character varying(255) NOT NULL
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
-- Name: booking; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.booking (
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "stockId" bigint NOT NULL,
    quantity integer NOT NULL,
    token character varying(6) NOT NULL,
    "userId" bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "isCancelled" boolean DEFAULT false NOT NULL,
    "isUsed" boolean DEFAULT false NOT NULL,
    "dateUsed" timestamp without time zone,
    "cancellationDate" timestamp without time zone,
    "confirmationDate" timestamp without time zone,
    "cancellationReason" public.cancellation_reason
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
-- Name: criterion; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.criterion (
    id bigint NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    "scoreDelta" integer NOT NULL,
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
-- Name: deposit; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.deposit (
    id bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "userId" bigint NOT NULL,
    source character varying(300) NOT NULL,
    "dateCreated" timestamp without time zone DEFAULT '1900-01-01 00:00:00'::timestamp without time zone NOT NULL,
    version smallint NOT NULL,
    "expirationDate" timestamp without time zone
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
-- Name: email; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.email (
    id bigint NOT NULL,
    content json NOT NULL,
    status public.emailstatus NOT NULL,
    datetime timestamp without time zone NOT NULL
);



--
-- Name: email_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.email_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: email_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.email_id_seq OWNED BY public.email.id;


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
    "isActive" boolean NOT NULL
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
-- Name: iris_france; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.iris_france (
    id bigint NOT NULL,
    "irisCode" character varying(9) NOT NULL,
    centroid public.geometry(Point) NOT NULL,
    shape public.geometry(Geometry,4326) NOT NULL
);



--
-- Name: iris_france_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.iris_france_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: iris_france_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.iris_france_id_seq OWNED BY public.iris_france.id;


--
-- Name: iris_venues; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.iris_venues (
    id bigint NOT NULL,
    "irisId" bigint NOT NULL,
    "venueId" bigint NOT NULL
);



--
-- Name: iris_venues_id_seq; Type: SEQUENCE; Schema: public; Owner: pass_culture
--

CREATE SEQUENCE public.iris_venues_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- Name: iris_venues_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pass_culture
--

ALTER SEQUENCE public.iris_venues_id_seq OWNED BY public.iris_venues.id;


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
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    "dateCreated" timestamp without time zone NOT NULL,
    "productId" bigint NOT NULL,
    "venueId" bigint NOT NULL,
    "lastProviderId" bigint,
    "bookingEmail" character varying(120) DEFAULT NULL::character varying,
    "isActive" boolean DEFAULT true NOT NULL,
    type character varying(50) NOT NULL,
    name character varying(140) NOT NULL,
    description text,
    conditions character varying(120),
    "ageMin" integer,
    "ageMax" integer,
    url character varying(255),
    "mediaUrls" character varying(220)[] NOT NULL,
    "durationMinutes" integer,
    "isNational" boolean NOT NULL,
    "extraData" json,
    "isDuo" boolean DEFAULT false NOT NULL,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "withdrawalDetails" text,
    "audioDisabilityCompliant" boolean,
    "mentalDisabilityCompliant" boolean,
    "motorDisabilityCompliant" boolean,
    "visualDisabilityCompliant" boolean,
    "externalTicketOfficeUrl" character varying,
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT offer_type_check CHECK (((type)::text <> 'None'::text))
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
-- Name: payment; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.payment (
    id bigint NOT NULL,
    author character varying(27) NOT NULL,
    comment text,
    "recipientName" character varying(140) NOT NULL,
    iban character varying(27),
    bic character varying(11),
    "bookingId" bigint NOT NULL,
    amount numeric(10,2) NOT NULL,
    "reimbursementRule" character varying(200) NOT NULL,
    "transactionEndToEndId" uuid,
    "recipientSiren" character varying(9) NOT NULL,
    "reimbursementRate" numeric(10,2) NOT NULL,
    "transactionLabel" character varying(140),
    "paymentMessageId" bigint
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
-- Name: product; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.product (
    "extraData" json,
    "thumbCount" integer NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    id bigint NOT NULL,
    type character varying(50) NOT NULL,
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
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL))),
    CONSTRAINT product_type_check CHECK (((type)::text <> 'None'::text))
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
    "apiKey" character(32),
    "apiKeyGenerationDate" timestamp without time zone,
    "enabledForPro" boolean DEFAULT false NOT NULL,
    "requireProviderIdentifier" boolean DEFAULT true NOT NULL,
    CONSTRAINT check_provider_has_localclass_or_apikey CHECK (((("localClass" IS NOT NULL) AND ("apiKey" IS NULL)) OR (("localClass" IS NULL) AND ("apiKey" IS NOT NULL))))
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
    "dateCreated" timestamp without time zone DEFAULT '1900-01-01 00:00:00'::timestamp without time zone NOT NULL,
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
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
    "expirationDate" timestamp without time zone
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
    "departementCode" character varying(3) NOT NULL,
    "isAdmin" boolean DEFAULT false NOT NULL,
    "resetPasswordToken" character varying(10),
    "resetPasswordTokenValidityLimit" timestamp without time zone,
    "firstName" character varying(128) DEFAULT ''::character varying,
    "lastName" character varying(128) DEFAULT ''::character varying,
    "postalCode" character varying(5) DEFAULT ''::character varying,
    "phoneNumber" character varying(20),
    "dateOfBirth" timestamp without time zone,
    "needsToFillCulturalSurvey" boolean DEFAULT true,
    "culturalSurveyId" uuid,
    civility character varying(20),
    activity character varying(128),
    "culturalSurveyFilledDate" timestamp without time zone,
    "hasSeenTutorials" boolean,
    address text,
    city character varying(100),
    "lastConnectionDate" timestamp without time zone,
    "isEmailValidated" boolean DEFAULT false,
    "isBeneficiary" boolean DEFAULT false NOT NULL,
    "hasAllowedRecommendations" boolean DEFAULT false NOT NULL,
    "suspensionReason" text,
    "isActive" boolean DEFAULT true,
    "hasSeenProTutorials" boolean DEFAULT false NOT NULL,
    CONSTRAINT check_admin_is_not_beneficiary CHECK ((("isBeneficiary" IS FALSE) OR ("isAdmin" IS FALSE)))
);



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
    rights public.rightstype
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
    "validationToken" character varying(27),
    "publicName" character varying(255),
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
    "venueTypeId" integer,
    "venueLabelId" integer,
    "dateCreated" timestamp without time zone,
    "isPermanent" boolean,
    CONSTRAINT "check_has_siret_xor_comment_xor_isVirtual" CHECK ((((siret IS NULL) AND (comment IS NULL) AND ("isVirtual" IS TRUE)) OR ((siret IS NULL) AND (comment IS NOT NULL) AND ("isVirtual" IS FALSE)) OR ((siret IS NOT NULL) AND ("isVirtual" IS FALSE)))),
    CONSTRAINT check_is_virtual_xor_has_address CHECK (((("isVirtual" IS TRUE) AND ((address IS NULL) AND ("postalCode" IS NULL) AND (city IS NULL) AND ("departementCode" IS NULL))) OR (("isVirtual" IS FALSE) AND (siret IS NOT NULL) AND (("postalCode" IS NOT NULL) AND (city IS NOT NULL) AND ("departementCode" IS NOT NULL))) OR (("isVirtual" IS FALSE) AND ((siret IS NULL) AND (comment IS NOT NULL)) AND ((address IS NOT NULL) AND ("postalCode" IS NOT NULL) AND (city IS NOT NULL) AND ("departementCode" IS NOT NULL))))),
    CONSTRAINT check_providable_with_provider_has_idatproviders CHECK ((("lastProviderId" IS NULL) OR ("idAtProviders" IS NOT NULL)))
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
-- Name: venue_provider; Type: TABLE; Schema: public; Owner: pass_culture
--

CREATE TABLE public.venue_provider (
    "isActive" boolean DEFAULT true NOT NULL,
    id bigint NOT NULL,
    "idAtProviders" character varying(70),
    "dateModifiedAtLastProvider" timestamp without time zone,
    "venueId" bigint NOT NULL,
    "providerId" bigint NOT NULL,
    "venueIdAtOfferProvider" character varying(70),
    "lastSyncDate" timestamp without time zone,
    "lastProviderId" bigint,
    "syncWorkerId" character varying(24),
    "fieldsUpdated" character varying(100)[] DEFAULT '{}'::character varying[] NOT NULL,
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
-- Name: activity id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.activity ALTER COLUMN id SET DEFAULT nextval('public.activity_id_seq'::regclass);


--
-- Name: allocine_pivot id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot ALTER COLUMN id SET DEFAULT nextval('public.allocine_pivot_id_seq'::regclass);


--
-- Name: allocine_venue_provider_price_rule id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_venue_provider_price_rule ALTER COLUMN id SET DEFAULT nextval('public.allocine_venue_provider_price_rule_id_seq'::regclass);


--
-- Name: api_key id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.api_key ALTER COLUMN id SET DEFAULT nextval('public.api_key_id_seq'::regclass);


--
-- Name: bank_information id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information ALTER COLUMN id SET DEFAULT nextval('public.bank_information_id_seq'::regclass);


--
-- Name: beneficiary_import id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_import_id_seq'::regclass);


--
-- Name: beneficiary_import_status id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.beneficiary_import_status ALTER COLUMN id SET DEFAULT nextval('public.beneficiary_import_status_id_seq'::regclass);


--
-- Name: booking id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.booking ALTER COLUMN id SET DEFAULT nextval('public.booking_id_seq'::regclass);


--
-- Name: criterion id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.criterion ALTER COLUMN id SET DEFAULT nextval('public.criterion_id_seq'::regclass);


--
-- Name: deposit id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit ALTER COLUMN id SET DEFAULT nextval('public.deposit_id_seq'::regclass);


--
-- Name: email id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.email ALTER COLUMN id SET DEFAULT nextval('public.email_id_seq'::regclass);


--
-- Name: favorite id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite ALTER COLUMN id SET DEFAULT nextval('public.favorite_id_seq'::regclass);


--
-- Name: feature id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.feature ALTER COLUMN id SET DEFAULT nextval('public.feature_id_seq'::regclass);


--
-- Name: iris_france id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_france ALTER COLUMN id SET DEFAULT nextval('public.iris_france_id_seq'::regclass);


--
-- Name: iris_venues id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_venues ALTER COLUMN id SET DEFAULT nextval('public.iris_venues_id_seq'::regclass);


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
-- Name: offerer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer ALTER COLUMN id SET DEFAULT nextval('public.offerer_id_seq'::regclass);


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
-- Name: product id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- Name: provider id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.provider ALTER COLUMN id SET DEFAULT nextval('public.provider_id_seq'::regclass);


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
-- Name: user_offerer id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer ALTER COLUMN id SET DEFAULT nextval('public.user_offerer_id_seq'::regclass);


--
-- Name: user_session id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_session ALTER COLUMN id SET DEFAULT nextval('public.user_session_id_seq'::regclass);


--
-- Name: venue id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue ALTER COLUMN id SET DEFAULT nextval('public.venue_id_seq'::regclass);


--
-- Name: venue_label id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_label ALTER COLUMN id SET DEFAULT nextval('public.venue_label_id_seq'::regclass);


--
-- Name: venue_provider id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider ALTER COLUMN id SET DEFAULT nextval('public.venue_provider_id_seq'::regclass);


--
-- Name: venue_type id; Type: DEFAULT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_type ALTER COLUMN id SET DEFAULT nextval('public.venue_type_id_seq'::regclass);


--
-- Data for Name: criterion; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.criterion (name, description, "scoreDelta")
VALUES
    ('Bonne offre d’appel', 'Offre déjà beaucoup réservée par les autres jeunes', 1),
    ('Mauvaise accroche', 'Offre ne possèdant pas une accroche de qualité suffisante', -1),
    ('Offre de médiation spécifique', 'Offre possédant une médiation orientée pour les jeunes de 18 ans', 2);



--
-- Data for Name: provider; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.provider ("isActive", name, "localClass", "apiKey", "apiKeyGenerationDate", "enabledForPro", "requireProviderIdentifier")
VALUES
    (false, 'TiteLive Stocks (Epagine / Place des libraires.com)', 'TiteLiveStocks', null, null, false, true),
    (false, 'TiteLive (Epagine / Place des libraires.com)', 'TiteLiveThings', null, null, false, true),
    (false, 'TiteLive (Epagine / Place des libraires.com) Descriptions', 'TiteLiveThingDescriptions', null, null, false, true),
    (false, 'TiteLive (Epagine / Place des libraires.com) Thumbs', 'TiteLiveThingThumbs', null, null, false, true),
    (false, 'Allociné', 'AllocineStocks', null, null, false, true),
    (false, 'Leslibraires.fr', 'LibrairesStocks', null, null, false, true),
    (false, 'FNAC', 'FnacStocks', null, null, false, true),
    (false, 'Praxiel/Inférence', 'PraxielStocks', null, null, false, true);


--
-- Data for Name: venue_type; Type: TABLE DATA; Schema: public; Owner: pass_culture
--

INSERT INTO public.venue_type (label)
VALUES
    ('Arts visuels, arts plastiques et galeries'),
    ('Centre culturel'),
    ('Cours et pratique artistiques'),
    ('Culture scientifique'),
    ('Festival'),
    ('Jeux / Jeux vidéos'),
    ('Librairie'),
    ('Bibliothèque ou médiathèque'),
    ('Musée'),
    ('Musique - Disquaire'),
    ('Musique - Magasin d’instruments'),
    ('Musique - Salle de concerts'),
    ('Offre numérique'),
    ('Patrimoine et tourisme'),
    ('Cinéma - Salle de projections'),
    ('Spectacle vivant'),
    ('Autre');

--
-- Name: activity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.activity_id_seq', 1, false);


--
-- Name: allocine_pivot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.allocine_pivot_id_seq', 1, false);


--
-- Name: allocine_venue_provider_price_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.allocine_venue_provider_price_rule_id_seq', 1, false);


--
-- Name: api_key_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.api_key_id_seq', 1, false);


--
-- Name: bank_information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.bank_information_id_seq', 1, false);


--
-- Name: beneficiary_import_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_import_id_seq', 1, false);


--
-- Name: beneficiary_import_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.beneficiary_import_status_id_seq', 1, false);


--
-- Name: booking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.booking_id_seq', 1, false);


--
-- Name: deposit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.deposit_id_seq', 1, false);


--
-- Name: email_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.email_id_seq', 1, false);


--
-- Name: favorite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.favorite_id_seq', 1, false);


--
-- Name: iris_france_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.iris_france_id_seq', 1, false);


--
-- Name: iris_venues_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.iris_venues_id_seq', 1, false);


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
-- Name: offerer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.offerer_id_seq', 1, false);


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
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.product_id_seq', 1, false);


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
-- Name: venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_id_seq', 1, false);


--
-- Name: venue_label_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_label_id_seq', 1, false);


--
-- Name: venue_provider_id_seq; Type: SEQUENCE SET; Schema: public; Owner: pass_culture
--

SELECT pg_catalog.setval('public.venue_provider_id_seq', 1, false);


--
-- Name: allocine_pivot allocine_pivot_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT allocine_pivot_pkey PRIMARY KEY (id);


--
-- Name: allocine_pivot allocine_pivot_siret_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT allocine_pivot_siret_key UNIQUE (siret);


--
-- Name: allocine_pivot allocine_pivot_theaterId_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.allocine_pivot
    ADD CONSTRAINT "allocine_pivot_theaterId_key" UNIQUE ("theaterId");


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
-- Name: bank_information bank_information_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.bank_information
    ADD CONSTRAINT bank_information_pkey PRIMARY KEY (id);


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
-- Name: product check_iscgucompatible_is_not_null; Type: CHECK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE public.product
    ADD CONSTRAINT check_iscgucompatible_is_not_null CHECK (("isGcuCompatible" IS NOT NULL)) NOT VALID;


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
-- Name: deposit deposit_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT deposit_pkey PRIMARY KEY (id);


--
-- Name: email email_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.email
    ADD CONSTRAINT email_pkey PRIMARY KEY (id);


--
-- Name: product event_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT "event_idAtProviders_key" UNIQUE ("idAtProviders");


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
-- Name: iris_france iris_france_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_france
    ADD CONSTRAINT iris_france_pkey PRIMARY KEY (id);


--
-- Name: iris_venues iris_venues_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_venues
    ADD CONSTRAINT iris_venues_pkey PRIMARY KEY (id);


--
-- Name: feature ix_feature_name; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.feature
    ADD CONSTRAINT ix_feature_name UNIQUE (name);


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
-- Name: offer offer_idAtProviders_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT "offer_idAtProviders_key" UNIQUE ("idAtProviders");


--
-- Name: offer offer_pkey; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_pkey PRIMARY KEY (id);


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
-- Name: offerer offerer_validationToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offerer
    ADD CONSTRAINT "offerer_validationToken_key" UNIQUE ("validationToken");


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
-- Name: favorite unique_favorite; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.favorite
    ADD CONSTRAINT unique_favorite UNIQUE ("userId", "offerId");


--
-- Name: user_offerer unique_user_offerer; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.user_offerer
    ADD CONSTRAINT unique_user_offerer UNIQUE ("userId", "offererId");


--
-- Name: venue_provider unique_venue_provider; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue_provider
    ADD CONSTRAINT unique_venue_provider UNIQUE ("venueId", "providerId", "venueIdAtOfferProvider");


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


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
-- Name: user user_resetPasswordToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_resetPasswordToken_key" UNIQUE ("resetPasswordToken");


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
-- Name: user user_validationToken_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT "user_validationToken_key" UNIQUE ("validationToken");


--
-- Name: venue validation_token_unique_key; Type: CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.venue
    ADD CONSTRAINT validation_token_unique_key UNIQUE ("validationToken");


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
-- Name: idx_beneficiary_import_application; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE UNIQUE INDEX idx_beneficiary_import_application ON public.beneficiary_import USING btree ("applicationId", "sourceId", source);


--
-- Name: idx_iris_france_centroid; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_iris_france_centroid ON public.iris_france USING gist (centroid);


--
-- Name: idx_iris_france_shape; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX idx_iris_france_shape ON public.iris_france USING gist (shape);


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
-- Name: ix_api_key_value; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_api_key_value ON public.api_key USING btree (value);


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
-- Name: ix_beneficiary_import_beneficiaryId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_import_beneficiaryId" ON public.beneficiary_import USING btree ("beneficiaryId");


--
-- Name: ix_beneficiary_import_status_beneficiaryImportId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_beneficiary_import_status_beneficiaryImportId" ON public.beneficiary_import_status USING btree ("beneficiaryImportId");


--
-- Name: ix_booking_stockId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_stockId" ON public.booking USING btree ("stockId");


--
-- Name: ix_booking_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_booking_userId" ON public.booking USING btree ("userId");


--
-- Name: ix_deposit_userId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_deposit_userId" ON public.deposit USING btree ("userId");


--
-- Name: ix_email_status; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_email_status ON public.email USING btree (status);


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
-- Name: ix_iris_venues_irisId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_iris_venues_irisId" ON public.iris_venues USING btree ("irisId");


--
-- Name: ix_mediation_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_mediation_offerId" ON public.mediation USING btree ("offerId");


--
-- Name: ix_offer_criterion_offerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_criterion_offerId" ON public.offer_criterion USING btree ("offerId");


--
-- Name: ix_offer_productId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_productId" ON public.offer USING btree ("productId");


--
-- Name: ix_offer_type; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_offer_type ON public.offer USING btree (type);


--
-- Name: ix_offer_venueId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_offer_venueId" ON public.offer USING btree ("venueId");


--
-- Name: ix_payment_bookingId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_bookingId" ON public.payment USING btree ("bookingId");


--
-- Name: ix_payment_status_paymentId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_payment_status_paymentId" ON public.payment_status USING btree ("paymentId");


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
-- Name: ix_user_lower_email; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX ix_user_lower_email ON public."user" USING btree (lower((email)::text));


--
-- Name: ix_user_offerer_offererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_user_offerer_offererId" ON public.user_offerer USING btree ("offererId");


--
-- Name: ix_venue_managingOffererId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_managingOffererId" ON public.venue USING btree ("managingOffererId");


--
-- Name: ix_venue_provider_providerId; Type: INDEX; Schema: public; Owner: pass_culture
--

CREATE INDEX "ix_venue_provider_providerId" ON public.venue_provider USING btree ("providerId");


--
-- Name: bank_information audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.bank_information REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: booking audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.booking REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offer audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.offer REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offerer audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.offerer REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: stock audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.stock REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: user audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public."user" REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity('{password,resetPasswordToken,validationToken}');


--
-- Name: venue audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.venue REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: venue_provider audit_trigger_delete; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_delete AFTER DELETE ON public.venue_provider REFERENCING OLD TABLE AS old_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: bank_information audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.bank_information REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: booking audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.booking REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offer audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.offer REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offerer audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.offerer REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: stock audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.stock REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: user audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public."user" REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity('{password,resetPasswordToken,validationToken}');


--
-- Name: venue audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.venue REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: venue_provider audit_trigger_insert; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_insert AFTER INSERT ON public.venue_provider REFERENCING NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: bank_information audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.bank_information REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: booking audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.booking REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offer audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.offer REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: offerer audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.offerer REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: stock audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.stock REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: user audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public."user" REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity('{password,resetPasswordToken,validationToken}');


--
-- Name: venue audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.venue REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: venue_provider audit_trigger_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER audit_trigger_update AFTER UPDATE ON public.venue_provider REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table FOR EACH STATEMENT WHEN ((current_setting('session_replication_role'::text) <> 'local'::text)) EXECUTE FUNCTION public.create_activity();


--
-- Name: booking booking_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE OF quantity, amount, "isCancelled", "isUsed", "userId" ON public.booking NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.check_booking();


--
-- Name: stock stock_update; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE CONSTRAINT TRIGGER stock_update AFTER INSERT OR UPDATE ON public.stock NOT DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW EXECUTE FUNCTION public.check_stock();


--
-- Name: booking stock_update_cancellation_date; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER stock_update_cancellation_date BEFORE INSERT OR UPDATE ON public.booking FOR EACH ROW EXECUTE FUNCTION public.save_cancellation_date();


--
-- Name: stock stock_update_modification_date; Type: TRIGGER; Schema: public; Owner: pass_culture
--

CREATE TRIGGER stock_update_modification_date BEFORE UPDATE ON public.stock FOR EACH ROW EXECUTE FUNCTION public.save_stock_modification_date();


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
-- Name: deposit deposit_userId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.deposit
    ADD CONSTRAINT "deposit_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


--
-- Name: product event_lastProviderId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT "event_lastProviderId_fkey" FOREIGN KEY ("lastProviderId") REFERENCES public.provider(id);


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
-- Name: iris_venues iris_venues_irisId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_venues
    ADD CONSTRAINT "iris_venues_irisId_fkey" FOREIGN KEY ("irisId") REFERENCES public.iris_france(id);


--
-- Name: iris_venues iris_venues_venueId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.iris_venues
    ADD CONSTRAINT "iris_venues_venueId_fkey" FOREIGN KEY ("venueId") REFERENCES public.venue(id);


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
-- Name: offer_criterion offer_criterion_criterionId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT "offer_criterion_criterionId_fkey" FOREIGN KEY ("criterionId") REFERENCES public.criterion(id);


--
-- Name: offer_criterion offer_criterion_offerId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.offer_criterion
    ADD CONSTRAINT "offer_criterion_offerId_fkey" FOREIGN KEY ("offerId") REFERENCES public.offer(id);


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
-- Name: payment payment_bookingId_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.payment
    ADD CONSTRAINT "payment_bookingId_fkey" FOREIGN KEY ("bookingId") REFERENCES public.booking(id);


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
-- Name: product product_owning_offerer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: pass_culture
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_owning_offerer_id_fkey FOREIGN KEY ("owningOffererId") REFERENCES public.offerer(id);


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
    ADD CONSTRAINT "token_userId_fkey" FOREIGN KEY ("userId") REFERENCES public."user"(id);


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

