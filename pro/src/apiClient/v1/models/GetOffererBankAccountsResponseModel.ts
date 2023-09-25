/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BankAccountResponseModel } from './BankAccountResponseModel';
import type { ManagedVenues } from './ManagedVenues';

export type GetOffererBankAccountsResponseModel = {
  bankAccounts: Array<BankAccountResponseModel>;
  hasPendingBankAccount: boolean;
  hasValidBankAccount: boolean;
  id: number;
  managedVenues: Array<ManagedVenues>;
  venuesWithNonFreeOffersWithoutBankAccounts: Array<number>;
};

