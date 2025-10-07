/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferTemplateAllowedAction } from './CollectiveOfferTemplateAllowedAction';
import type { GetCollectiveOfferLocationModel } from './GetCollectiveOfferLocationModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { TemplateDatesModel } from './TemplateDatesModel';
export type CollectiveOfferTemplateResponseModel = {
  allowedActions: Array<CollectiveOfferTemplateAllowedAction>;
  dates?: TemplateDatesModel | null;
  displayedStatus: CollectiveOfferDisplayedStatus;
  id: number;
  imageUrl?: string | null;
  isActive: boolean;
  location: GetCollectiveOfferLocationModel;
  name: string;
  venue: ListOffersVenueResponseModel;
};

