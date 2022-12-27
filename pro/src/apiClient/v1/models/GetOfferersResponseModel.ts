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
  nonHumanizedId: number;
  siren?: string | null;
  userHasAccess: boolean;
};

