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

import type { ArtistsResponseModel, ValidationError } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Artists<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetArtists
   * @summary get_artists <GET>
   * @request GET:/artists
   */
  getArtists = (
    query: {
      /** Search */
      search: string
    },
    params: RequestParams = {}
  ) =>
    this.request<ArtistsResponseModel, void | ValidationError>({
      path: `/artists`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
}
