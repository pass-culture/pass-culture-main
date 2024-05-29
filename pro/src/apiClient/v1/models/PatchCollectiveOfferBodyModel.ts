/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { EacFormat } from './EacFormat';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type PatchCollectiveOfferBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmails?: Array<string> | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  description?: string | null;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  formats?: Array<EacFormat> | null;
  interventionArea?: Array<string> | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  nationalProgramId?: number | null;
  offerVenue?: CollectiveOfferVenueBodyModel | null;
  students?: Array<StudentLevels> | null;
  subcategoryId?: (SubcategoryIdEnum | string) | null;
  venueId?: number | null;
  visualDisabilityCompliant?: boolean | null;
};

