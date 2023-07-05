/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type StockResponseModel = {
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  dateCreated: string;
  dateModified: string;
  hasActivationCodes: boolean;
  id: number;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  price: number;
  quantity?: number | null;
};

