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
  id: string;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  offerId: string;
  price: number;
  quantity?: number | null;
};

