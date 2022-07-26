/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type InvoiceResponseModel = {
  amount: number;
  businessUnitName?: string | null;
  cashflowLabels: Array<string>;
  date: string;
  reference: string;
  reimbursementPointName?: string | null;
  url: string;
};

