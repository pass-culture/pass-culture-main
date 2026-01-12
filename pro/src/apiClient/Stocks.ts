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
  EventStocksBulkCreateBodyModel,
  EventStocksBulkUpdateBodyModel,
  GetStocksResponseModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Stocks<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name BulkUpdateEventStocks
   * @summary bulk_update_event_stocks <PATCH>
   * @request PATCH:/stocks/bulk
   */
  bulkUpdateEventStocks = (
    data: EventStocksBulkUpdateBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetStocksResponseModel, void | ValidationError>({
      path: `/stocks/bulk`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name BulkCreateEventStocks
   * @summary bulk_create_event_stocks <POST>
   * @request POST:/stocks/bulk
   */
  bulkCreateEventStocks = (
    data: EventStocksBulkCreateBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetStocksResponseModel, void | ValidationError>({
      path: `/stocks/bulk`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
}
