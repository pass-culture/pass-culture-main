/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOffersBookingResponseModel } from './CollectiveOffersBookingResponseModel';
import type { CollectiveOffersStockResponseModel } from './CollectiveOffersStockResponseModel';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type CollectiveOfferResponseModel = {
  allowedActions: (Array<CollectiveOfferAllowedAction> | Array<CollectiveOfferTemplateAllowedAction>);
  booking?: CollectiveOffersBookingResponseModel | null;
  dates?: TemplateDatesModel | null;
  displayedStatus: CollectiveOfferDisplayedStatus;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  imageUrl?: string | null;
  isActive: boolean;
  isEducational: boolean;
  isShowcase: boolean;
  location?: GetCollectiveOfferLocationModel | null;
  name: string;
  stocks: Array<CollectiveOffersStockResponseModel>;
  venue: ListOffersVenueResponseModel;
};

