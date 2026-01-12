/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

import type {
  FinanceBankAccountListResponseModel,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Finance<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetBankAccounts
   * @summary get_bank_accounts <GET>
   * @request GET:/finance/bank-accounts
   */
  getBankAccounts = (params: RequestParams = {}) =>
    this.request<FinanceBankAccountListResponseModel, void | ValidationError>({
      path: `/finance/bank-accounts`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetCombinedInvoices
   * @summary get_combined_invoices <GET>
   * @request GET:/finance/combined-invoices
   */
  getCombinedInvoices = (
    query: {
      /** Invoicereferences */
      invoiceReferences: string[]
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/finance/combined-invoices`,
      method: 'GET',
      query: query,
      ...params,
    })
}
