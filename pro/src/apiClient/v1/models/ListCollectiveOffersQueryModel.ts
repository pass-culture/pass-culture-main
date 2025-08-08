/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveLocationType } from './CollectiveLocationType';
import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferType } from './CollectiveOfferType';
import type { EacFormat } from './EacFormat';
export type ListCollectiveOffersQueryModel = {
  collectiveOfferType?: CollectiveOfferType | null;
  format?: EacFormat | null;
  locationType?: CollectiveLocationType | null;
  nameOrIsbn?: string | null;
  offererAddressId?: number | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: Array<CollectiveOfferDisplayedStatus> | null;
  venueId?: number | null;
};

