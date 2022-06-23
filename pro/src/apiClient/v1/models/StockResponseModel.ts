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
  educationalPriceDetail?: string | null;
  hasActivationCodes: boolean;
  id: string;
  isEducationalStockEditable?: boolean | null;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  numberOfTickets?: number | null;
  offerId: string;
  price: number;
  quantity?: number | null;
};

