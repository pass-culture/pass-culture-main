/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BankAccountApplicationStatus } from './BankAccountApplicationStatus';
import type { LinkedVenue } from './LinkedVenue';
export type BankAccountResponseModel = {
  dateCreated: string;
  dsApplicationId: (number | null);
  id: number;
  isActive: boolean;
  label: string;
  linkedVenues: Array<LinkedVenue>;
  obfuscatedIban: string;
  status: BankAccountApplicationStatus;
};

