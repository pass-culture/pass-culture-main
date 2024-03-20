/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EacFormat } from './EacFormat';
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
  formats?: Array<EacFormat> | null;
  imageCredit?: string | null;
  imageFile?: string | null;
  interventionArea?: Array<string> | null;
  isActive?: boolean | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  nationalProgramId?: number | null;
  numberOfTickets?: number | null;
  offerVenue?: OfferVenueModel | null;
  students?: Array<string> | null;
  subcategoryId?: string | null;
  totalPrice?: number | null;
  venueId?: number | null;
  visualDisabilityCompliant?: boolean | null;
};

