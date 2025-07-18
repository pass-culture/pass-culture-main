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
  hasPartnerPage: boolean;
  hasPendingBankAccount: boolean;
  hasValidBankAccount: boolean;
  id: number;
  isActive: boolean;
  isCaledonian: boolean;
  isOnboarded: boolean;
  isValidated: boolean;
  managedVenues?: Array<GetOffererVenueResponseModel>;
  name: string;
  postalCode: string;
  siren: string;
  street?: string | null;
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>;
};

