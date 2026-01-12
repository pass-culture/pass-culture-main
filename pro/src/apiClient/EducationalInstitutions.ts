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
  EducationalInstitutionsResponseModel,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class EducationalInstitutions<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetEducationalInstitutions
   * @summary get_educational_institutions <GET>
   * @request GET:/educational_institutions
   */
  getEducationalInstitutions = (
    query?: {
      /**
       * Perpagelimit
       * @default 1000
       */
      perPageLimit?: number
      /**
       * Page
       * @default 1
       */
      page?: number
    },
    params: RequestParams = {}
  ) =>
    this.request<EducationalInstitutionsResponseModel, void | ValidationError>({
      path: `/educational_institutions`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
}
