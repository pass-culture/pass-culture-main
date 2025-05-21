/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOffersBookingResponseModel } from './CollectiveOffersBookingResponseModel';
import type { CollectiveOffersStockResponseModel } from './CollectiveOffersStockResponseModel';
import type { CollectiveOfferStatus } from './CollectiveOfferStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { EacFormat } from './EacFormat';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { NationalProgramModel } from './NationalProgramModel';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type CollectiveOfferResponseModel = {
  allowedActions: (Array<CollectiveOfferAllowedAction> | Array<CollectiveOfferTemplateAllowedAction>);
  booking?: CollectiveOffersBookingResponseModel | null;
  dates?: TemplateDatesModel | null;
  displayedStatus: CollectiveOfferDisplayedStatus;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  formats: Array<EacFormat>;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageCredit?: string | null;
  imageUrl?: string | null;
  interventionArea: Array<string>;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isPublicApi: boolean;
  isShowcase: boolean;
  name: string;
  nationalProgram?: NationalProgramModel | null;
  status: CollectiveOfferStatus;
  stocks: Array<CollectiveOffersStockResponseModel>;
  templateId?: string | null;
  venue: ListOffersVenueResponseModel;
};

