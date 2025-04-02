/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferLocationModel } from './CollectiveOfferLocationModel';
import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { EacFormat } from './EacFormat';
import type { StudentLevels } from './StudentLevels';
export type PostCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmails: Array<string>;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description: string;
  domains: Array<number>;
  durationMinutes?: number | null;
  formats: Array<EacFormat>;
  interventionArea?: Array<string> | null;
  location?: CollectiveOfferLocationModel | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  nationalProgramId?: number | null;
  offerVenue?: CollectiveOfferVenueBodyModel | null;
  students: Array<StudentLevels>;
  subcategoryId?: string | null;
  templateId?: number | null;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};

