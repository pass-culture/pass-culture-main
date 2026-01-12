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

import type { GetProductInformations, ValidationError } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class GetProductByEan<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetProductByEan
   * @summary get_product_by_ean <GET>
   * @request GET:/get_product_by_ean/{ean}/{offerer_id}
   */
  getProductByEan = (
    ean: string,
    offererId: number,
    params: RequestParams = {}
  ) =>
    this.request<GetProductInformations, void | ValidationError>({
      path: `/get_product_by_ean/${ean}/${offererId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
