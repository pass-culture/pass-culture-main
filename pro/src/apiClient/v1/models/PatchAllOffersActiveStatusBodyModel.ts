/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfferStatus } from './OfferStatus';
export type PatchAllOffersActiveStatusBodyModel = {
  categoryId?: string | null;
  creationMode?: string | null;
  isActive: boolean;
  nameOrIsbn?: string | null;
  offererAddressId?: number | null;
  offererId?: number | null;
  periodBeginningDate?: string | null;
  periodEndingDate?: string | null;
  status?: OfferStatus | null;
  venueId?: number | null;
};

