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
  VenuesEducationalStatusesResponseModel,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class VenuesEducationalStatuses<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetVenuesEducationalStatuses
   * @summary get_venues_educational_statuses <GET>
   * @request GET:/venues-educational-statuses
   */
  getVenuesEducationalStatuses = (params: RequestParams = {}) =>
    this.request<
      VenuesEducationalStatusesResponseModel,
      void | ValidationError
    >({
      path: `/venues-educational-statuses`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
