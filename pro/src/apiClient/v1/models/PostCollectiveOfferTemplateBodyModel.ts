/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferLocationModelV2 } from './CollectiveOfferLocationModelV2';
import type { EacFormat } from './EacFormat';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { PostDateRangeModel } from './PostDateRangeModel';
import type { StudentLevels } from './StudentLevels';
export type PostCollectiveOfferTemplateBodyModel = {
  audioDisabilityCompliant: boolean;
  bookingEmails: Array<string>;
  contactEmail?: (string | null);
  contactForm?: (OfferContactFormEnum | null);
  contactPhone?: (string | null);
  contactUrl?: (string | null);
  dates?: (PostDateRangeModel | null);
  description: string;
  domains: Array<number>;
  durationMinutes?: (number | null);
  formats: Array<EacFormat>;
  interventionArea: (Array<string> | null);
  location: CollectiveOfferLocationModelV2;
  mentalDisabilityCompliant: boolean;
  motorDisabilityCompliant: boolean;
  name: string;
  nationalProgramId?: (number | null);
  priceDetail?: (string | null);
  students: Array<StudentLevels>;
  templateId?: (number | null);
  venueId: number;
  visualDisabilityCompliant: boolean;
};

