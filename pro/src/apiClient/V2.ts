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
  GetIndividualOfferResponseModel,
  HasInvoiceResponseModel,
  InvoiceListV2ResponseModel,
  PostOfferBodyModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class V2<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name HasInvoice
   * @summary has_invoice <GET>
   * @request GET:/v2/finance/has-invoice
   */
  hasInvoice = (
    query: {
      /** Offererid */
      offererId: number
    },
    params: RequestParams = {}
  ) =>
    this.request<HasInvoiceResponseModel, void | ValidationError>({
      path: `/v2/finance/has-invoice`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetInvoicesV2
   * @summary get_invoices_v2 <GET>
   * @request GET:/v2/finance/invoices
   */
  getInvoicesV2 = (
    query?: {
      /**
       * Periodbeginningdate
       * @default null
       */
      periodBeginningDate?: string | null
      /**
       * Periodendingdate
       * @default null
       */
      periodEndingDate?: string | null
      /**
       * Bankaccountid
       * @default null
       */
      bankAccountId?: number | null
      /**
       * Offererid
       * @default null
       */
      offererId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<InvoiceListV2ResponseModel, void | ValidationError>({
      path: `/v2/finance/invoices`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateOffer
   * @summary create_offer <POST>
   * @request POST:/v2/offers
   */
  createOffer = (data: PostOfferBodyModel, params: RequestParams = {}) =>
    this.request<GetIndividualOfferResponseModel, void | ValidationError>({
      path: `/v2/offers`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetReimbursementsCsvV2
   * @summary get_reimbursements_csv_v2 <GET>
   * @request GET:/v2/reimbursements/csv
   */
  getReimbursementsCsvV2 = (
    query: {
      /**
       * Invoicesreferences
       * @maxItems 75
       * @uniqueItems true
       */
      invoicesReferences: string[]
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/v2/reimbursements/csv`,
      method: 'GET',
      query: query,
      ...params,
    })
}
