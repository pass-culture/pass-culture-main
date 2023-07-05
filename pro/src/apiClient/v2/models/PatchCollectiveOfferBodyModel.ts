/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { OfferVenueModel } from './OfferVenueModel';

export type PatchCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  beginningDatetime?: string | null;
  bookingEmails?: Array<string> | null;
  bookingLimitDatetime?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description?: string | null;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  educationalInstitution?: string | null;
  educationalInstitutionId?: number | null;
  educationalPriceDetail?: string | null;
  imageCredit?: string | null;
  imageFile?: string | null;
  interventionArea?: Array<string> | null;
  isActive?: boolean | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  numberOfTickets?: number | null;
  offerVenue?: OfferVenueModel | null;
  students?: Array<string> | null;
  subcategoryId?: string | null;
  totalPrice?: number | null;
  venueId?: number | null;
  visualDisabilityCompliant?: boolean | null;
};

