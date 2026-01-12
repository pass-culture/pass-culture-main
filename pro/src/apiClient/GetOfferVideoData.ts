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

import type { ValidationError, VideoData } from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class GetOfferVideoData<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetOfferVideoMetadata
   * @summary get_offer_video_metadata <GET>
   * @request GET:/get-offer-video-data
   */
  getOfferVideoMetadata = (
    query: {
      /**
       * Videourl
       * @format uri
       * @minLength 1
       * @maxLength 2083
       */
      videoUrl: string
    },
    params: RequestParams = {}
  ) =>
    this.request<VideoData, void | ValidationError>({
      path: `/get-offer-video-data`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
}
