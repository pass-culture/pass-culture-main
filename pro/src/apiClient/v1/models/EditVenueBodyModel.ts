/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { VenueContactModel } from './VenueContactModel';

export type EditVenueBodyModel = {
  address?: string | null;
  audioDisabilityCompliant?: boolean | null;
  bookingEmail?: string | null;
  city?: string | null;
  comment?: string | null;
  contact?: VenueContactModel | null;
  description?: string | null;
  isAccessibilityAppliedOnAllOffers?: boolean | null;
  isEmailAppliedOnAllOffers?: boolean | null;
  isWithdrawalAppliedOnAllOffers?: boolean | null;
  latitude?: (number | string) | null;
  longitude?: (number | string) | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  postalCode?: string | null;
  publicName?: string | null;
  reimbursementPointId?: number | null;
  shouldSendMail?: boolean | null;
  siret?: string | null;
  venueLabelId?: number | null;
  venueTypeCode?: string | null;
  visualDisabilityCompliant?: boolean | null;
  withdrawalDetails?: string | null;
};

