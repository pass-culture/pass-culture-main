/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetOffererVenueResponseModel } from './GetOffererVenueResponseModel';
import type { OffererApiKey } from './OffererApiKey';
export type GetOffererResponseModel = {
  allowedOnAdage: boolean;
  apiKey: OffererApiKey;
  city: string;
  dateCreated: string;
  hasActiveOffer: boolean;
  hasAvailablePricingPoints: boolean;
  hasBankAccountWithPendingCorrections: boolean;
  hasDigitalVenueAtLeastOneOffer: boolean;
  hasHeadlineOffer: boolean;
  hasNonFreeOffer: boolean;
  hasPendingBankAccount: boolean;
  hasValidBankAccount: boolean;
  id: number;
  isActive: boolean;
  isOnboarded: boolean;
  isOnboardingOngoing: boolean;
  isValidated: boolean;
  managedVenues?: Array<GetOffererVenueResponseModel>;
  name: string;
  postalCode: string;
  siren?: string | null;
  street?: string | null;
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>;
};

