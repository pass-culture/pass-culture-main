/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { DatesModel } from './DatesModel';
import type { EacFormat } from './EacFormat';
import type { GetCollectiveOfferLocationModelV2 } from './GetCollectiveOfferLocationModelV2';
import type { GetCollectiveOfferVenueResponseModel } from './GetCollectiveOfferVenueResponseModel';
import type { NationalProgramResponseModel } from './NationalProgramResponseModel';
import type { OfferContactFormEnum } from './OfferContactFormEnum';
import type { OfferDomain } from './OfferDomain';
import type { StudentLevels } from './StudentLevels';
export type GetCollectiveOfferTemplateResponseModel = {
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>;
  audioDisabilityCompliant: (boolean | null);
  bookingEmails: Array<string>;
  contactEmail: (string | null);
  contactForm: (OfferContactFormEnum | null);
  contactPhone: (string | null);
  contactUrl: (string | null);
  dateCreated: string;
  dates: (DatesModel | null);
  description: string;
  displayedStatus: CollectiveOfferDisplayedStatus;
  domains: Array<OfferDomain>;
  durationMinutes: (number | null);
  educationalPriceDetail: (string | null);
  formats: Array<EacFormat>;
  id: number;
  imageCredit: (string | null);
  imageUrl: (string | null);
  interventionArea: Array<string>;
  isTemplate?: boolean;
  location: GetCollectiveOfferLocationModelV2;
  mentalDisabilityCompliant: (boolean | null);
  motorDisabilityCompliant: (boolean | null);
  name: string;
  nationalProgram: (NationalProgramResponseModel | null);
  students: Array<StudentLevels>;
  venue: GetCollectiveOfferVenueResponseModel;
  visualDisabilityCompliant: (boolean | null);
};

