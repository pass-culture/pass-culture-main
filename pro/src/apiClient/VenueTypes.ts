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
  VenueTypeListResponseModel,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class VenueTypes<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetVenueTypes
   * @summary get_venue_types <GET>
   * @request GET:/venue-types
   */
  getVenueTypes = (params: RequestParams = {}) =>
    this.request<VenueTypeListResponseModel, void | ValidationError>({
      path: `/venue-types`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
