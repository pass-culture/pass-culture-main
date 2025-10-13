/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDatesModel } from './CollectiveOfferDatesModel';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
export type CollectiveOfferTemplateResponseModel = {
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>;
  dates?: CollectiveOfferDatesModel | null;
  displayedStatus: CollectiveOfferDisplayedStatus;
  id: number;
  imageUrl?: string | null;
  location: GetCollectiveOfferLocationModel;
  name: string;
  venue: ListOffersVenueResponseModel;
};

