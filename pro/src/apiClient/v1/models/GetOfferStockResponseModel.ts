/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type GetOfferStockResponseModel = {
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  dateCreated: string;
  dateModified: string;
  hasActivationCode: boolean;
  id: number;
  isBookable: boolean;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  isSoftDeleted: boolean;
  price: number;
  priceCategoryId?: number | null;
  quantity?: number | null;
  remainingQuantity?: (number | string) | null;
};

