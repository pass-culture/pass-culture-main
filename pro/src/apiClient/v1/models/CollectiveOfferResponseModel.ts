/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferAllowedAction } from './CollectiveOfferAllowedAction';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferStockResponseModel } from './CollectiveOfferStockResponseModel';
import type { DatesModel } from './DatesModel';
import type { EducationalInstitutionResponseModelV2 } from './EducationalInstitutionResponseModelV2';
import type { GetCollectiveOfferLocationModelV2 } from './GetCollectiveOfferLocationModelV2';
import type { ListOffersVenueResponseModelV2 } from './ListOffersVenueResponseModelV2';
export type CollectiveOfferResponseModel = {
  allowedActions: Array<CollectiveOfferAllowedAction>;
  dates: (DatesModel | null);
  displayedStatus: CollectiveOfferDisplayedStatus;
  educationalInstitution: (EducationalInstitutionResponseModelV2 | null);
  id: number;
  imageUrl: (string | null);
  location: GetCollectiveOfferLocationModelV2;
  name: string;
  stock: (CollectiveOfferStockResponseModel | null);
  venue: ListOffersVenueResponseModelV2;
};

