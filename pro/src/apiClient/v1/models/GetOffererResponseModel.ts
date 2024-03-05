/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetOffererVenueResponseModel } from './GetOffererVenueResponseModel';
import type { OffererApiKey } from './OffererApiKey';
export type GetOffererResponseModel = {
  address?: string | null;
  allowedOnAdage: boolean;
  apiKey: OffererApiKey;
  city: string;
  dateCreated: string;
  demarchesSimplifieesApplicationId?: string | null;
  hasActiveOffer: boolean;
  hasAvailablePricingPoints: boolean;
  hasDigitalVenueAtLeastOneOffer: boolean;
  hasNonFreeOffer: boolean;
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

