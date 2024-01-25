/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferOfferVenue } from './CollectiveOfferOfferVenue';
import type { EacFormat } from './EacFormat';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type CollectiveOfferTemplateResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  contactEmail: string;
  contactPhone?: string | null;
  dates?: TemplateDatesModel | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalPriceDetail?: string | null;
  formats?: Array<EacFormat> | null;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isExpired: boolean;
  isFavorite?: boolean | null;
  isSoldOut: boolean;
  isTemplate?: boolean;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  offerId?: number | null;
  offerVenue: CollectiveOfferOfferVenue;
  students: Array<StudentLevels>;
  subcategoryLabel: string;
  venue: OfferVenueResponse;
  visualDisabilityCompliant?: boolean | null;
};

