/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { CollectiveOfferType } from './CollectiveOfferType';

export type ListOffersQueryModel = {
  categoryId?: string | null;
  collectiveOfferType?: CollectiveOfferType | null;
  creationMode?: string | null;
  nameOrIsbn?: string | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: string | null;
  venueId?: number | null;
};

