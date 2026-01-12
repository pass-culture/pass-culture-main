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
  GetVenueListLiteResponseModel,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Lite<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetVenuesLite
   * @summary get_venues_lite <GET>
   * @request GET:/lite/venues
   */
  getVenuesLite = (
    query?: {
      /** Validated */
      validated?: boolean | null
      /** Activeofferersonly */
      activeOfferersOnly?: boolean | null
      /** Offererid */
      offererId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<GetVenueListLiteResponseModel, void | ValidationError>({
      path: `/lite/venues`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
}
