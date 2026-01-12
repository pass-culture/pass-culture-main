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
  ListFeatureResponseModel,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Features<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name ListFeatures
   * @summary list_features <GET>
   * @request GET:/features
   */
  listFeatures = (params: RequestParams = {}) =>
    this.request<ListFeatureResponseModel, void | ValidationError>({
      path: `/features`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
