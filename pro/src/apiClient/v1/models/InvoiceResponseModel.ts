/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type InvoiceResponseModel = {
  amount: number;
  cashflowLabels: Array<string>;
  date: string;
  reference: string;
  reimbursementPointName?: string | null;
  url: string;
};

