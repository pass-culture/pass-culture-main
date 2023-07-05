/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOffererVenueResponseModel } from './GetOffererVenueResponseModel';
import type { OffererApiKey } from './OffererApiKey';

export type GetOffererResponseModel = {
  address?: string | null;
  apiKey: OffererApiKey;
  city: string;
  dateCreated: string;
  dateModifiedAtLastProvider?: string | null;
  demarchesSimplifieesApplicationId?: string | null;
  fieldsUpdated: Array<string>;
  hasAvailablePricingPoints: boolean;
  hasDigitalVenueAtLeastOneOffer: boolean;
  id: number;
  idAtProviders?: string | null;
  isActive: boolean;
  isValidated: boolean;
  lastProviderId?: string | null;
  managedVenues?: Array<GetOffererVenueResponseModel>;
  name: string;
  postalCode: string;
  siren?: string | null;
};

