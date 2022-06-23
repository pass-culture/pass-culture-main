/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type GetOfferStockResponseModel = {
  beginningDatetime?: string | null;
  bookingLimitDatetime?: string | null;
  bookingsQuantity: number;
  cancellationLimitDate?: string | null;
  dateCreated: string;
  dateModified: string;
  dateModifiedAtLastProvider?: string | null;
  fieldsUpdated: Array<string>;
  hasActivationCode: boolean;
  id: string;
  idAtProviders?: string | null;
  isBookable: boolean;
  isEventDeletable: boolean;
  isEventExpired: boolean;
  isSoftDeleted: boolean;
  lastProviderId?: string | null;
  offerId: string;
  price: number;
  quantity?: number | null;
  remainingQuantity?: (number | string) | null;
};

