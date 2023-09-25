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
  demarchesSimplifieesApplicationId?: string | null;
  dsToken?: string | null;
  hasAvailablePricingPoints: boolean;
  hasDigitalVenueAtLeastOneOffer: boolean;
  hasPendingBankAccount: boolean;
  hasValidBankAccount: boolean;
  id: number;
  isActive: boolean;
  isValidated: boolean;
  managedVenues?: Array<GetOffererVenueResponseModel>;
  name: string;
  postalCode: string;
  siren?: string | null;
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>;
};

