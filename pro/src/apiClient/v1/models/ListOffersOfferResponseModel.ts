/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ListOffersStockResponseModel } from './ListOffersStockResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type ListOffersOfferResponseModel = {
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isShowcase?: boolean | null;
  isThing: boolean;
  name: string;
  productIsbn?: string | null;
  status: OfferStatus;
  stocks: Array<ListOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  venue: ListOffersVenueResponseModel;
};

