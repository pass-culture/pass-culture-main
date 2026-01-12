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
  ListProviderResponse,
  ListVenueProviderResponse,
  PostVenueProviderBody,
  ValidationError,
  VenueProviderResponse,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class VenueProviders<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name ListVenueProviders
   * @summary list_venue_providers <GET>
   * @request GET:/venueProviders
   */
  listVenueProviders = (
    query: {
      /** Venueid */
      venueId: number
    },
    params: RequestParams = {}
  ) =>
    this.request<ListVenueProviderResponse, void | ValidationError>({
      path: `/venueProviders`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateVenueProvider
   * @summary create_venue_provider <POST>
   * @request POST:/venueProviders
   */
  createVenueProvider = (
    data: PostVenueProviderBody,
    params: RequestParams = {}
  ) =>
    this.request<VenueProviderResponse, void | ValidationError>({
      path: `/venueProviders`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name UpdateVenueProvider
   * @summary update_venue_provider <PUT>
   * @request PUT:/venueProviders
   */
  updateVenueProvider = (
    data: PostVenueProviderBody,
    params: RequestParams = {}
  ) =>
    this.request<VenueProviderResponse, void | ValidationError>({
      path: `/venueProviders`,
      method: 'PUT',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetProvidersByVenue
   * @summary get_providers_by_venue <GET>
   * @request GET:/venueProviders/{venue_id}
   */
  getProvidersByVenue = (venueId: number, params: RequestParams = {}) =>
    this.request<ListProviderResponse, void | ValidationError>({
      path: `/venueProviders/${venueId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteVenueProvider
   * @summary delete_venue_provider <DELETE>
   * @request DELETE:/venueProviders/{venue_provider_id}
   */
  deleteVenueProvider = (venueProviderId: number, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/venueProviders/${venueProviderId}`,
      method: 'DELETE',
      ...params,
    })
}
