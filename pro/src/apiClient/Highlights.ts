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

import type { HighlightsResponseModel, ValidationError } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Highlights<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetHighlights
   * @summary get_highlights <GET>
   * @request GET:/highlights
   */
  getHighlights = (params: RequestParams = {}) =>
    this.request<HighlightsResponseModel, void | ValidationError>({
      path: `/highlights`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
