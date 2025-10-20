/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDatesModel } from './CollectiveOfferDatesModel';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferStockResponseModel } from './CollectiveOfferStockResponseModel';
import type { EducationalInstitutionResponseModel } from './EducationalInstitutionResponseModel';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
export type CollectiveOfferBookableResponseModel = {
  allowedActions: Array<CollectiveOfferAllowedAction>;
  dates?: CollectiveOfferDatesModel | null;
  displayedStatus: CollectiveOfferDisplayedStatus;
  educationalInstitution?: EducationalInstitutionResponseModel | null;
  id: number;
  imageUrl?: string | null;
  location: GetCollectiveOfferLocationModel;
  name: string;
  stock?: CollectiveOfferStockResponseModel | null;
  venue: ListOffersVenueResponseModel;
};

