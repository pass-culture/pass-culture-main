/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferOfferVenueResponseModel } from './CollectiveOfferOfferVenueResponseModel';
import type { EacFormat } from './EacFormat';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { OfferDomain } from './OfferDomain';
import type { OfferStatus } from './OfferStatus';
import type { StudentLevels } from './StudentLevels';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
import type { TemplateDatesModel } from './TemplateDatesModel';

export type GetCollectiveOfferTemplateResponseModel = {
  audioDisabilityCompliant?: boolean | null;
  bookingEmails: Array<string>;
  contactEmail: string;
  contactPhone?: string | null;
  dateCreated: string;
  dates?: TemplateDatesModel | null;
  description: string;
  domains: Array<OfferDomain>;
  durationMinutes?: number | null;
  educationalPriceDetail?: string | null;
  formats?: Array<EacFormat> | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isCancellable: boolean;
  isEditable: boolean;
  isNonFreeOffer?: boolean | null;
  mentalDisabilityCompliant?: boolean | null;
  motorDisabilityCompliant?: boolean | null;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  offerId?: number | null;
  offerVenue: CollectiveOfferOfferVenueResponseModel;
  status: OfferStatus;
  students: Array<StudentLevels>;
  subcategoryId?: SubcategoryIdEnum | null;
  venue: GetCollectiveOfferVenueResponseModel;
  visualDisabilityCompliant?: boolean | null;
};

