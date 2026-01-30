/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDatesModel } from './CollectiveOfferDatesModel';
import type { EacFormat } from './EacFormat';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { OfferDomain } from './OfferDomain';
import type { OfferVenueResponse } from './OfferVenueResponse';
import type { StudentLevels } from './StudentLevels';
export type CollectiveOfferTemplateResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  contactEmail?: string | null;
  contactForm?: OfferContactFormEnum | null;
  contactPhone?: string | null;
  contactUrl?: string | null;
  dates?: CollectiveOfferDatesModel | null;
  description?: string | null;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalPriceDetail?: string | null;
  formats: Array<EacFormat>;
  id: number;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isFavorite?: boolean | null;
  isTemplate: boolean;
  location?: GetCollectiveOfferLocationModel | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  students: Array<StudentLevels>;
  venue: OfferVenueResponse;
  visualDisabilityCompliant?: boolean | null;
};

