/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetOffererVenueResponseModel } from './GetOffererVenueResponseModel';
export type GetOffererResponseModel = {
  allowedOnAdage: boolean;
  canDisplayHighlights: boolean;
  hasActiveOffer: boolean;
  hasAvailablePricingPoints: boolean;
  hasBankAccountWithPendingCorrections: boolean;
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
  siren: string;
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>;
};

