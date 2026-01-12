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
  CategoriesResponseModel,
  CollectiveOfferDisplayedStatus,
  CreateOfferHighlightRequestBodyModel,
  CreateThumbnailBodyModel,
  CreateThumbnailResponseModel,
  DeleteOfferRequestBody,
  DeleteStockListBody,
  GetActiveEANOfferResponseModel,
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  GetMusicTypesResponse,
  GetStocksResponseModel,
  HeadLineOfferResponseModel,
  HeadlineOfferCreationBodyModel,
  HeadlineOfferDeleteBodyModel,
  ListOffersResponseModel,
  MinimalPostOfferBodyModel,
  OfferOpeningHoursSchema,
  OfferStatus,
  PatchAllOffersActiveStatusBodyModel,
  PatchOfferActiveStatusBodyModel,
  PatchOfferBodyModel,
  PatchOfferPublishBodyModel,
  PriceCategoryBody,
  StockStatsResponseModel,
  StocksOrderedBy,
  ThingStocksBulkUpsertBodyModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Offers<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name ListOffers
   * @summary list_offers <GET>
   * @request GET:/offers
   */
  listOffers = (
    query?: {
      /** Nameorisbn */
      nameOrIsbn?: string | null
      /** Offererid */
      offererId?: number | null
      /** Status */
      status?: OfferStatus | CollectiveOfferDisplayedStatus | null
      /** Venueid */
      venueId?: number | null
      /** Categoryid */
      categoryId?: string | null
      /** Creationmode */
      creationMode?: string | null
      /**
       * Periodbeginningdate
       * @format date
       */
      periodBeginningDate?: string | null
      /**
       * Periodendingdate
       * @format date
       */
      periodEndingDate?: string | null
      /** Offereraddressid */
      offererAddressId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<ListOffersResponseModel, void | ValidationError>({
      path: `/offers`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PostOffer
   * @summary post_offer <POST>
   * @request POST:/offers
   */
  postOffer = (data: MinimalPostOfferBodyModel, params: RequestParams = {}) =>
    this.request<GetIndividualOfferResponseModel, void | ValidationError>({
      path: `/offers`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchOffersActiveStatus
   * @summary patch_offers_active_status <PATCH>
   * @request PATCH:/offers/active-status
   */
  patchOffersActiveStatus = (
    data: PatchOfferActiveStatusBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offers/active-status`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchAllOffersActiveStatus
   * @summary patch_all_offers_active_status <PATCH>
   * @request PATCH:/offers/all-active-status
   */
  patchAllOffersActiveStatus = (
    data: PatchAllOffersActiveStatusBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offers/all-active-status`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetCategories
   * @summary get_categories <GET>
   * @request GET:/offers/categories
   */
  getCategories = (params: RequestParams = {}) =>
    this.request<CategoriesResponseModel, void | ValidationError>({
      path: `/offers/categories`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteDraftOffers
   * @summary delete_draft_offers <POST>
   * @request POST:/offers/delete-draft
   */
  deleteDraftOffers = (
    data: DeleteOfferRequestBody,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offers/delete-draft`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteHeadlineOffer
   * @summary delete_headline_offer <POST>
   * @request POST:/offers/delete_headline
   */
  deleteHeadlineOffer = (
    data: HeadlineOfferDeleteBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offers/delete_headline`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetMusicTypes
   * @summary get_music_types <GET>
   * @request GET:/offers/music-types
   */
  getMusicTypes = (params: RequestParams = {}) =>
    this.request<GetMusicTypesResponse, void | ValidationError>({
      path: `/offers/music-types`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchPublishOffer
   * @summary patch_publish_offer <PATCH>
   * @request PATCH:/offers/publish
   */
  patchPublishOffer = (
    data: PatchOfferPublishBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetIndividualOfferResponseModel, void | ValidationError>({
      path: `/offers/publish`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateThumbnail
   * @summary create_thumbnail <POST>
   * @request POST:/offers/thumbnails
   */
  createThumbnail = (
    data: CreateThumbnailBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<CreateThumbnailResponseModel, void | ValidationError>({
      path: `/offers/thumbnails`,
      method: 'POST',
      body: data,
      type: ContentType.FormData,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteThumbnail
   * @summary delete_thumbnail <DELETE>
   * @request DELETE:/offers/thumbnails/{offer_id}
   */
  deleteThumbnail = (offerId: number, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/offers/thumbnails/${offerId}`,
      method: 'DELETE',
      ...params,
    })
  /**
   * No description
   *
   * @name UpsertHeadlineOffer
   * @summary upsert_headline_offer <POST>
   * @request POST:/offers/upsert_headline
   */
  upsertHeadlineOffer = (
    data: HeadlineOfferCreationBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<HeadLineOfferResponseModel, void | ValidationError>({
      path: `/offers/upsert_headline`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffer
   * @summary get_offer <GET>
   * @request GET:/offers/{offer_id}
   */
  getOffer = (offerId: number, params: RequestParams = {}) =>
    this.request<
      GetIndividualOfferWithAddressResponseModel,
      void | ValidationError
    >({
      path: `/offers/${offerId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchOffer
   * @summary patch_offer <PATCH>
   * @request PATCH:/offers/{offer_id}
   */
  patchOffer = (
    offerId: number,
    data: PatchOfferBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<
      GetIndividualOfferWithAddressResponseModel,
      void | ValidationError
    >({
      path: `/offers/${offerId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PostHighlightRequestOffer
   * @summary post_highlight_request_offer <POST>
   * @request POST:/offers/{offer_id}/highlight-requests
   */
  postHighlightRequestOffer = (
    offerId: number,
    data: CreateOfferHighlightRequestBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<
      GetIndividualOfferWithAddressResponseModel,
      void | ValidationError
    >({
      path: `/offers/${offerId}/highlight-requests`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOfferOpeningHours
   * @summary get_offer_opening_hours <GET>
   * @request GET:/offers/{offer_id}/opening-hours
   */
  getOfferOpeningHours = (offerId: number, params: RequestParams = {}) =>
    this.request<OfferOpeningHoursSchema, void | ValidationError>({
      path: `/offers/${offerId}/opening-hours`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * @description For each day of the week, there can be at most two pairs of timespans (opening hours start and end). Week days might have null/empty opening hours: in that case, no data will be inserted. This allows a more flexible way to send data. The output data will always contain every week day. If no opening hours has been set, the timespan data will be null. Note: since opening hours should always be erased before any new data is inserted, this route can also be used as a DELETE one.
   *
   * @name UpsertOfferOpeningHours
   * @summary Create or update an offer's opening hours (erase existing if any)
   * @request PATCH:/offers/{offer_id}/opening-hours
   */
  upsertOfferOpeningHours = (
    offerId: number,
    data: OfferOpeningHoursSchema,
    params: RequestParams = {}
  ) =>
    this.request<OfferOpeningHoursSchema, void | ValidationError>({
      path: `/offers/${offerId}/opening-hours`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * @description - If a price category exists in the DB but not in `price_categories`, it is deleted. - Otherwise, price categories are updated or created as needed.
   *
   * @name ReplaceOfferPriceCategories
   * @summary Replace all price categories of an offer.
   * @request PUT:/offers/{offer_id}/price_categories
   */
  replaceOfferPriceCategories = (
    offerId: number,
    data: PriceCategoryBody,
    params: RequestParams = {}
  ) =>
    this.request<
      GetIndividualOfferWithAddressResponseModel,
      void | ValidationError
    >({
      path: `/offers/${offerId}/price_categories`,
      method: 'PUT',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetStocksStats
   * @summary get_stocks_stats <GET>
   * @request GET:/offers/{offer_id}/stocks-stats
   */
  getStocksStats = (offerId: number, params: RequestParams = {}) =>
    this.request<StockStatsResponseModel, void | ValidationError>({
      path: `/offers/${offerId}/stocks-stats`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetStocks
   * @summary get_stocks <GET>
   * @request GET:/offers/{offer_id}/stocks/
   */
  getStocks = (
    offerId: number,
    query?: {
      /**
       * Date
       * @format date
       */
      date?: string | null
      /**
       * Time
       * @format time
       */
      time?: string | null
      /** Price Category Id */
      price_category_id?: number | null
      /** @default "BEGINNING_DATETIME" */
      order_by?: StocksOrderedBy
      /**
       * Order By Desc
       * @default false
       */
      order_by_desc?: boolean
      /**
       * Page
       * @min 1
       * @default 1
       */
      page?: number
      /**
       * Stocks Limit Per Page
       * @default 20
       */
      stocks_limit_per_page?: number
    },
    params: RequestParams = {}
  ) =>
    this.request<GetStocksResponseModel, void | ValidationError>({
      path: `/offers/${offerId}/stocks/`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * @description - If a stock exists in the DB but not in `stocks`, it is soft-deleted. - Otherwise, stocks are updated or created as needed.
   *
   * @name UpsertOfferStocks
   * @summary Upsert all price categories stocks of a non-event offer.
   * @request PATCH:/offers/{offer_id}/stocks/
   */
  upsertOfferStocks = (
    offerId: number,
    data: ThingStocksBulkUpsertBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetStocksResponseModel, void | ValidationError>({
      path: `/offers/${offerId}/stocks/`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteStocks
   * @summary delete_stocks <POST>
   * @request POST:/offers/{offer_id}/stocks/delete
   */
  deleteStocks = (
    offerId: number,
    data: DeleteStockListBody,
    params: RequestParams = {}
  ) =>
    this.request<GetStocksResponseModel, void | ValidationError>({
      path: `/offers/${offerId}/stocks/delete`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetActiveVenueOfferByEan
   * @summary get_active_venue_offer_by_ean <GET>
   * @request GET:/offers/{venue_id}/ean/{ean}
   */
  getActiveVenueOfferByEan = (
    venueId: number,
    ean: string,
    params: RequestParams = {}
  ) =>
    this.request<GetActiveEANOfferResponseModel, void | ValidationError>({
      path: `/offers/${venueId}/ean/${ean}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
