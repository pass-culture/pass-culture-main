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
  GetOffersStatsResponseModel,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Venue<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetOffersStatistics
   * @summary get_offers_statistics <GET>
   * @request GET:/venue/{venue_id}/offers-statistics
   */
  getOffersStatistics = (venueId: number, params: RequestParams = {}) =>
    this.request<GetOffersStatsResponseModel, void | ValidationError>({
      path: `/venue/${venueId}/offers-statistics`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
