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
  ValidationError,
  VenueLabelListResponseModel,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class VenueLabels<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name FetchVenueLabels
   * @summary fetch_venue_labels <GET>
   * @request GET:/venue-labels
   */
  fetchVenueLabels = (params: RequestParams = {}) =>
    this.request<VenueLabelListResponseModel, void | ValidationError>({
      path: `/venue-labels`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
