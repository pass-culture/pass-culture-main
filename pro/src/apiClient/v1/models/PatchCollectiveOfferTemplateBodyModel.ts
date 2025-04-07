/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferLocationModel } from './CollectiveOfferLocationModel';
import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { DateRangeModel } from './DateRangeModel';
import type { EacFormat } from './EacFormat';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { StudentLevels } from './StudentLevels';
export type PatchCollectiveOfferTemplateBodyModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmails?: Array<string> | null;
  contactEmail?: string | null;
  contactForm?: OfferContactFormEnum | null;
  contactPhone?: string | null;
  contactUrl?: string | null;
  dates?: DateRangeModel | null;
  description?: string | null;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  formats?: Array<EacFormat> | null;
  interventionArea?: Array<string> | null;
  location?: CollectiveOfferLocationModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name?: string | null;
  nationalProgramId?: number | null;
  offerVenue?: CollectiveOfferVenueBodyModel | null;
  priceDetail?: string | null;
  students?: Array<StudentLevels> | null;
  venueId?: number | null;
  visualDisabilityCompliant?: boolean | null;
};

