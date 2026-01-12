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

import type { StatisticsModel, ValidationError } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class GetStatistics<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetStatistics
   * @summary get_statistics <GET>
   * @request GET:/get-statistics
   */
  getStatistics = (
    query?: {
      /**
       * Venueids
       * @default []
       */
      venueIds?: number[]
    },
    params: RequestParams = {}
  ) =>
    this.request<StatisticsModel, void | ValidationError>({
      path: `/get-statistics`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
}
