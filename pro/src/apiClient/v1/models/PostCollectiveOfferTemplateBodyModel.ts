/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferVenueBodyModel } from './CollectiveOfferVenueBodyModel';
import type { DateRangeOnCreateModel } from './DateRangeOnCreateModel';
import type { EacFormat } from './EacFormat';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { StudentLevels } from './StudentLevels';
export type PostCollectiveOfferTemplateBodyModel = {
  audioDisabilityCompliant?: boolean;
  bookingEmails: Array<string>;
  contactEmail?: string | null;
  contactForm?: OfferContactFormEnum | null;
  contactPhone?: string | null;
  contactUrl?: string | null;
  dates?: DateRangeOnCreateModel | null;
  description: string;
  domains?: Array<number> | null;
  durationMinutes?: number | null;
  formats?: Array<EacFormat> | null;
  interventionArea?: Array<string> | null;
  mentalDisabilityCompliant?: boolean;
  motorDisabilityCompliant?: boolean;
  name: string;
  nationalProgramId?: number | null;
  offerVenue: CollectiveOfferVenueBodyModel;
  offererId?: string | null;
  priceDetail?: string | null;
  students: Array<StudentLevels>;
  subcategoryId?: string | null;
  templateId?: number | null;
  venueId: number;
  visualDisabilityCompliant?: boolean;
};

