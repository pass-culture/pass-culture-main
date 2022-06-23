/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ListOffersStockResponseModel } from './ListOffersStockResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';

export type ListOffersOfferResponseModel = {
  hasBookingLimitDatetimesPassed: boolean;
  id: string;
  isActive: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isShowcase?: boolean | null;
  isThing: boolean;
  name: string;
  productIsbn?: string | null;
  status: string;
  stocks: Array<ListOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  venue: ListOffersVenueResponseModel;
  venueId: string;
};

