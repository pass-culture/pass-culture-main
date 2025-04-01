/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { EacFormat } from './EacFormat';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { OfferDomain } from './OfferDomain';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type CollectiveOfferTemplateResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  contactEmail?: string | null;
  contactForm?: OfferContactFormEnum | null;
  contactPhone?: string | null;
  contactUrl?: string | null;
  dates?: TemplateDatesModel | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalPriceDetail?: string | null;
  formats: Array<EacFormat>;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isExpired: boolean;
  isFavorite?: boolean | null;
  isSoldOut: boolean;
  isTemplate: boolean;
  location?: GetCollectiveOfferLocationModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  offerVenue: CollectiveOfferOfferVenue;
  students: Array<StudentLevels>;
  venue: OfferVenueResponse;
  visualDisabilityCompliant?: boolean | null;
};

