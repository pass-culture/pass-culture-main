/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProviderResponse } from './ProviderResponse';
export type VenueProviderResponse = {
  dateCreated: string;
  id: number;
  isActive: boolean;
  isDuo: (boolean | null);
  isFromAllocineProvider: boolean;
  lastSyncDate: (string | null);
  price?: (number | null);
  provider: ProviderResponse;
  quantity?: (number | null);
  venueId: number;
  venueIdAtOfferProvider: (string | null);
};

