/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { DatesModel } from './DatesModel';
import type { GetCollectiveOfferLocationModelV2 } from './GetCollectiveOfferLocationModelV2';
import type { ListOffersVenueResponseModelV2 } from './ListOffersVenueResponseModelV2';
export type CollectiveOfferTemplateResponseModel = {
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>;
  dates: (DatesModel | null);
  displayedStatus: CollectiveOfferDisplayedStatus;
  id: number;
  imageUrl: (string | null);
  location: GetCollectiveOfferLocationModelV2;
  name: string;
  venue: ListOffersVenueResponseModelV2;
};

