/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityNotOpenToPublic } from './ActivityNotOpenToPublic';
import type { ActivityOpenToPublic } from './ActivityOpenToPublic';
import type { VenueContactModelV2 } from './VenueContactModelV2';
import type { WeekdayOpeningHoursTimespans } from './WeekdayOpeningHoursTimespans';
export type EditVenueBodyModel = {
  activity?: (ActivityOpenToPublic | ActivityNotOpenToPublic | null);
  audioDisabilityCompliant?: (boolean | null);
  banId?: (string | null);
  bookingEmail?: (string | null);
  city?: (string | null);
  comment?: (string | null);
  contact?: (VenueContactModelV2 | null);
  culturalDomains?: (Array<string> | null);
  description?: (string | null);
  inseeCode?: (string | null);
  isAccessibilityAppliedOnAllOffers?: (boolean | null);
  isManualEdition?: (boolean | null);
  isOpenToPublic?: (boolean | null);
  latitude?: ((number | string) | null);
  longitude?: ((number | string) | null);
  mentalDisabilityCompliant?: (boolean | null);
  motorDisabilityCompliant?: (boolean | null);
  name?: (string | null);
  openingHours?: (WeekdayOpeningHoursTimespans | null);
  postalCode?: (string | null);
  publicName?: (string | null);
  siret?: (string | null);
  street?: (string | null);
  venueLabelId?: (number | null);
  visualDisabilityCompliant?: (boolean | null);
  volunteeringUrl?: (string | null);
  withdrawalDetails?: (string | null);
};

