/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OpeningHoursModel } from './OpeningHoursModel';
import type { VenueContactModel } from './VenueContactModel';
import type { VenueTypeCode } from './VenueTypeCode';
export type EditVenueBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  banId?: string | null;
  bookingEmail?: string | null;
  city?: string | null;
  comment?: string | null;
  contact?: VenueContactModel | null;
  description?: string | null;
  inseeCode?: string | null;
  isAccessibilityAppliedOnAllOffers?: boolean | null;
  isManualEdition?: boolean | null;
  isOpenToPublic?: boolean | null;
  latitude?: number | null;
  longitude?: number | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  openingHours?: Array<OpeningHoursModel> | null;
  postalCode?: string | null;
  publicName?: string | null;
  siret?: string | null;
  street?: string | null;
  venueLabelId?: number | null;
  venueTypeCode?: VenueTypeCode | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};

