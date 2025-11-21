/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ListOffersStockResponseModel } from './ListOffersStockResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { LocationResponseModel } from './LocationResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { ShortHighlightResponseModel } from './ShortHighlightResponseModel';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type ListOffersOfferResponseModel = {
  bookingAllowedDatetime?: string | null;
  bookingsCount?: number | null;
  canBeEvent: boolean;
  hasBookingLimitDatetimesPassed: boolean;
  highlightRequests: Array<ShortHighlightResponseModel>;
  id: number;
  isActive: boolean;
  isDigital: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isHeadlineOffer: boolean;
  isShowcase?: boolean | null;
  isThing: boolean;
  location?: LocationResponseModel | null;
  name: string;
  productId?: number | null;
  productIsbn?: string | null;
  publicationDatetime?: string | null;
  status: OfferStatus;
  stocks: Array<ListOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  venue: ListOffersVenueResponseModel;
};

