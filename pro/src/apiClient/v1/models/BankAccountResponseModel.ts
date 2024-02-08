/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BankAccountApplicationStatus } from './BankAccountApplicationStatus';
import type { LinkedVenues } from './LinkedVenues';
export type BankAccountResponseModel = {
  bic: string;
  dateCreated: string;
  dateLastStatusUpdate?: string | null;
  dsApplicationId?: number | null;
  id: number;
  isActive: boolean;
  label: string;
  linkedVenues: Array<LinkedVenues>;
  obfuscatedIban: string;
  status: BankAccountApplicationStatus;
};

