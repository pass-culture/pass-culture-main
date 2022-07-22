/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GetOffererVenueResponseModel } from './GetOffererVenueResponseModel';
import type { OffererApiKey } from './OffererApiKey';

export type GetOffererResponseModel = {
  address?: string | null;
  apiKey: OffererApiKey;
  bic?: string | null;
  city: string;
  dateCreated: string;
  dateModifiedAtLastProvider?: string | null;
  demarchesSimplifieesApplicationId?: string | null;
  fieldsUpdated: Array<string>;
  hasAvailablePricingPoints: boolean;
  hasDigitalVenueAtLeastOneOffer: boolean;
  hasMissingBankInformation: boolean;
  iban?: string | null;
  id: string;
  idAtProviders?: string | null;
  isActive: boolean;
  isValidated: boolean;
  lastProviderId?: string | null;
  managedVenues?: Array<GetOffererVenueResponseModel>;
  name: string;
  nonHumanizedId: number;
  postalCode: string;
  siren?: string | null;
};

