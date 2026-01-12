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
  EditVenueBodyModel,
  EditVenueCollectiveDataBodyModel,
  GetVenueListResponseModel,
  GetVenueResponseModel,
  GetVenuesOfOffererFromSiretResponseModel,
  LinkVenueToPricingPointBodyModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Venues<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * @description This route loads way too much data.
   *
   * @name GetVenues
   * @summary [deprecated] please use /lite/venues instead
   * @request GET:/venues
   * @deprecated
   */
  getVenues = (
    query?: {
      /** Validated */
      validated?: boolean | null
      /** Activeofferersonly */
      activeOfferersOnly?: boolean | null
      /** Offererid */
      offererId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<GetVenueListResponseModel, void | ValidationError>({
      path: `/venues`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetVenuesOfOffererFromSiret
   * @summary get_venues_of_offerer_from_siret <GET>
   * @request GET:/venues/siret/{siret}
   */
  getVenuesOfOffererFromSiret = (siret: string, params: RequestParams = {}) =>
    this.request<
      GetVenuesOfOffererFromSiretResponseModel,
      void | ValidationError
    >({
      path: `/venues/siret/${siret}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetVenue
   * @summary get_venue <GET>
   * @request GET:/venues/{venue_id}
   */
  getVenue = (venueId: number, params: RequestParams = {}) =>
    this.request<GetVenueResponseModel, void | ValidationError>({
      path: `/venues/${venueId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name EditVenue
   * @summary edit_venue <PATCH>
   * @request PATCH:/venues/{venue_id}
   */
  editVenue = (
    venueId: number,
    data: EditVenueBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetVenueResponseModel, void | ValidationError>({
      path: `/venues/${venueId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteVenueBanner
   * @summary delete_venue_banner <DELETE>
   * @request DELETE:/venues/{venue_id}/banner
   */
  deleteVenueBanner = (venueId: number, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/venues/${venueId}/banner`,
      method: 'DELETE',
      ...params,
    })
  /**
   * No description
   *
   * @name EditVenueCollectiveData
   * @summary edit_venue_collective_data <PATCH>
   * @request PATCH:/venues/{venue_id}/collective-data
   */
  editVenueCollectiveData = (
    venueId: number,
    data: EditVenueCollectiveDataBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetVenueResponseModel, void | ValidationError>({
      path: `/venues/${venueId}/collective-data`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name LinkVenueToPricingPoint
   * @summary link_venue_to_pricing_point <POST>
   * @request POST:/venues/{venue_id}/pricing-point
   */
  linkVenueToPricingPoint = (
    venueId: number,
    data: LinkVenueToPricingPointBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/venues/${venueId}/pricing-point`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
}
