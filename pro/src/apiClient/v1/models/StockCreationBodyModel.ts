/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type StockCreationBodyModel = {
  activationCodes?: Array<string> | null;
  activationCodesExpirationDatetime?: string | null;
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  price: number;
  quantity?: number | null;
};

