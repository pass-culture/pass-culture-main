/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferDisplayedStatus } from './CollectiveOfferDisplayedStatus';
import type { CollectiveOfferType } from './CollectiveOfferType';

export type ListCollectiveOffersQueryModel = {
  categoryId?: string | null;
  collectiveOfferType?: CollectiveOfferType | null;
  creationMode?: string | null;
  nameOrIsbn?: string | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: CollectiveOfferDisplayedStatus | null;
  venueId?: number | null;
};

