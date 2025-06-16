/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddressResponseIsLinkedToVenueModel } from './AddressResponseIsLinkedToVenueModel';
import type { ListOffersStockResponseModel } from './ListOffersStockResponseModel';
import type { ListOffersVenueResponseModel } from './ListOffersVenueResponseModel';
import type { OfferStatus } from './OfferStatus';
import type { SubcategoryIdEnum } from './SubcategoryIdEnum';
export type ListOffersOfferResponseModel = {
  address?: AddressResponseIsLinkedToVenueModel | null;
  bookingAllowedDatetime?: string | null;
  hasBookingLimitDatetimesPassed: boolean;
  id: number;
  isActive: boolean;
  isDigital: boolean;
  isEditable: boolean;
  isEducational: boolean;
  isEvent: boolean;
  isHeadlineOffer: boolean;
  isShowcase?: boolean | null;
  isThing: boolean;
  name: string;
  productIsbn?: string | null;
  publicationDatetime?: string | null;
  status: OfferStatus;
  stocks: Array<ListOffersStockResponseModel>;
  subcategoryId: SubcategoryIdEnum;
  thumbUrl?: string | null;
  venue: ListOffersVenueResponseModel;
};

