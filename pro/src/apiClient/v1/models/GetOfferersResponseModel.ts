/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOfferersVenueResponseModel } from './GetOfferersVenueResponseModel';

export type GetOfferersResponseModel = {
  id: string;
  isValidated: boolean;
  managedVenues: Array<GetOfferersVenueResponseModel>;
  nOffers: number;
  name: string;
  siren?: string | null;
  userHasAccess: boolean;
};

