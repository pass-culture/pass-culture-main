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

import type { StructureDataBodyModel, ValidationError } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Structure<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetStructureData
   * @summary get_structure_data <GET>
   * @request GET:/structure/search/{search_input}
   */
  getStructureData = (searchInput: string, params: RequestParams = {}) =>
    this.request<StructureDataBodyModel, void | ValidationError>({
      path: `/structure/search/${searchInput}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
