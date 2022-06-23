/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ProviderResponse } from './ProviderResponse';

export type VenueProviderResponse = {
  dateModifiedAtLastProvider?: string;
  fieldsUpdated: Array<string>;
  id: string;
  idAtProviders?: string;
  isActive: boolean;
  isDuo?: boolean;
  isFromAllocineProvider: boolean;
  lastProviderId?: string;
  lastSyncDate?: string;
  nOffers: number;
  price?: number;
  provider: ProviderResponse;
  providerId: string;
  quantity?: number;
  venueId: string;
  venueIdAtOfferProvider: string;
};

