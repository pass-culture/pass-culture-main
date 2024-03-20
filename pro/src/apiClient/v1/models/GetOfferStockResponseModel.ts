/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type GetOfferStockResponseModel = {
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  hasActivationCode: boolean;
  id: number;
  isEventDeletable: boolean;
  price: number;
  priceCategoryId?: number | null;
  quantity?: number | null;
  remainingQuantity?: (number | string) | null;
};

