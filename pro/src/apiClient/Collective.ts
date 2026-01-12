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
  AttachImageFormModel,
  AttachImageResponseModel,
  CollectiveLocationType,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseIdModel,
  CollectiveStockCreationBodyModel,
  CollectiveStockEditionBodyModel,
  CollectiveStockResponseModel,
  EacFormat,
  EducationalDomainsResponseModel,
  EducationalRedactors,
  GetCollectiveOfferRequestResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  ListCollectiveOffersResponseModel,
  ListCollectiveOfferTemplatesResponseModel,
  PatchCollectiveOfferActiveStatusBodyModel,
  PatchCollectiveOfferArchiveBodyModel,
  PatchCollectiveOfferBodyModel,
  PatchCollectiveOfferEducationalInstitution,
  PatchCollectiveOfferTemplateBodyModel,
  PostCollectiveOfferBodyModel,
  PostCollectiveOfferTemplateBodyModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Collective<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetCollectiveOffers
   * @summary get_collective_offers <GET>
   * @request GET:/collective/bookable-offers
   */
  getCollectiveOffers = (
    query?: {
      /** Name */
      name?: string | null
      /** Offererid */
      offererId?: number | null
      status?: CollectiveOfferDisplayedStatus[] | null
      /** Venueid */
      venueId?: number | null
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
      format?: EacFormat | null
      locationType?: CollectiveLocationType | null
      /** Offereraddressid */
      offererAddressId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<ListCollectiveOffersResponseModel, void | ValidationError>({
      path: `/collective/bookable-offers`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name ListEducationalDomains
   * @summary list_educational_domains <GET>
   * @request GET:/collective/educational-domains
   */
  listEducationalDomains = (params: RequestParams = {}) =>
    this.request<EducationalDomainsResponseModel, void | ValidationError>({
      path: `/collective/educational-domains`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateCollectiveOffer
   * @summary create_collective_offer <POST>
   * @request POST:/collective/offers
   */
  createCollectiveOffer = (
    data: PostCollectiveOfferBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<CollectiveOfferResponseIdModel, void | ValidationError>({
      path: `/collective/offers`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOfferTemplates
   * @summary get_collective_offer_templates <GET>
   * @request GET:/collective/offers-template
   */
  getCollectiveOfferTemplates = (
    query?: {
      /** Name */
      name?: string | null
      /** Offererid */
      offererId?: number | null
      status?: CollectiveOfferDisplayedStatus[] | null
      /** Venueid */
      venueId?: number | null
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
      format?: EacFormat | null
      locationType?: CollectiveLocationType | null
      /** Offereraddressid */
      offererAddressId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<
      ListCollectiveOfferTemplatesResponseModel,
      void | ValidationError
    >({
      path: `/collective/offers-template`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateCollectiveOfferTemplate
   * @summary create_collective_offer_template <POST>
   * @request POST:/collective/offers-template
   */
  createCollectiveOfferTemplate = (
    data: PostCollectiveOfferTemplateBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<CollectiveOfferResponseIdModel, void | ValidationError>({
      path: `/collective/offers-template`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOffersTemplateActiveStatus
   * @summary patch_collective_offers_template_active_status <PATCH>
   * @request PATCH:/collective/offers-template/active-status
   */
  patchCollectiveOffersTemplateActiveStatus = (
    data: PatchCollectiveOfferActiveStatusBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers-template/active-status`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOffersTemplateArchive
   * @summary patch_collective_offers_template_archive <PATCH>
   * @request PATCH:/collective/offers-template/archive
   */
  patchCollectiveOffersTemplateArchive = (
    data: PatchCollectiveOfferArchiveBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers-template/archive`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOfferRequest
   * @summary get_collective_offer_request <GET>
   * @request GET:/collective/offers-template/request/{request_id}
   */
  getCollectiveOfferRequest = (requestId: number, params: RequestParams = {}) =>
    this.request<
      GetCollectiveOfferRequestResponseModel,
      void | ValidationError
    >({
      path: `/collective/offers-template/request/${requestId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOfferTemplate
   * @summary get_collective_offer_template <GET>
   * @request GET:/collective/offers-template/{offer_id}
   */
  getCollectiveOfferTemplate = (offerId: number, params: RequestParams = {}) =>
    this.request<
      GetCollectiveOfferTemplateResponseModel,
      void | ValidationError
    >({
      path: `/collective/offers-template/${offerId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name EditCollectiveOfferTemplate
   * @summary edit_collective_offer_template <PATCH>
   * @request PATCH:/collective/offers-template/{offer_id}
   */
  editCollectiveOfferTemplate = (
    offerId: number,
    data: PatchCollectiveOfferTemplateBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<
      GetCollectiveOfferTemplateResponseModel,
      void | ValidationError
    >({
      path: `/collective/offers-template/${offerId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteOfferTemplateImage
   * @summary delete_offer_template_image <DELETE>
   * @request DELETE:/collective/offers-template/{offer_id}/image
   */
  deleteOfferTemplateImage = (offerId: number, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers-template/${offerId}/image`,
      method: 'DELETE',
      ...params,
    })
  /**
   * No description
   *
   * @name AttachOfferTemplateImage
   * @summary attach_offer_template_image <POST>
   * @request POST:/collective/offers-template/{offer_id}/image
   */
  attachOfferTemplateImage = (
    offerId: number,
    data: AttachImageFormModel,
    params: RequestParams = {}
  ) =>
    this.request<AttachImageResponseModel, void | ValidationError>({
      path: `/collective/offers-template/${offerId}/image`,
      method: 'POST',
      body: data,
      type: ContentType.FormData,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOfferTemplatePublication
   * @summary patch_collective_offer_template_publication <PATCH>
   * @request PATCH:/collective/offers-template/{offer_id}/publish
   */
  patchCollectiveOfferTemplatePublication = (
    offerId: number,
    params: RequestParams = {}
  ) =>
    this.request<
      GetCollectiveOfferTemplateResponseModel,
      void | ValidationError
    >({
      path: `/collective/offers-template/${offerId}/publish`,
      method: 'PATCH',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOffersArchive
   * @summary patch_collective_offers_archive <PATCH>
   * @request PATCH:/collective/offers/archive
   */
  patchCollectiveOffersArchive = (
    data: PatchCollectiveOfferArchiveBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers/archive`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOffersCsv
   * @summary get_collective_offers_csv <GET>
   * @request GET:/collective/offers/csv
   */
  getCollectiveOffersCsv = (
    query?: {
      /** Name */
      name?: string | null
      /** Offererid */
      offererId?: number | null
      status?: CollectiveOfferDisplayedStatus[] | null
      /** Venueid */
      venueId?: number | null
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
      format?: EacFormat | null
      locationType?: CollectiveLocationType | null
      /** Offereraddressid */
      offererAddressId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers/csv`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOffersExcel
   * @summary get_collective_offers_excel <GET>
   * @request GET:/collective/offers/excel
   */
  getCollectiveOffersExcel = (
    query?: {
      /** Name */
      name?: string | null
      /** Offererid */
      offererId?: number | null
      status?: CollectiveOfferDisplayedStatus[] | null
      /** Venueid */
      venueId?: number | null
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
      format?: EacFormat | null
      locationType?: CollectiveLocationType | null
      /** Offereraddressid */
      offererAddressId?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers/excel`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name GetAutocompleteEducationalRedactorsForUai
   * @summary get_autocomplete_educational_redactors_for_uai <GET>
   * @request GET:/collective/offers/redactors
   */
  getAutocompleteEducationalRedactorsForUai = (
    query: {
      /**
       * Uai
       * @minLength 3
       */
      uai: string
      /**
       * Candidate
       * @minLength 3
       */
      candidate: string
    },
    params: RequestParams = {}
  ) =>
    this.request<EducationalRedactors, void | ValidationError>({
      path: `/collective/offers/redactors`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetCollectiveOffer
   * @summary get_collective_offer <GET>
   * @request GET:/collective/offers/{offer_id}
   */
  getCollectiveOffer = (offerId: number, params: RequestParams = {}) =>
    this.request<GetCollectiveOfferResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name EditCollectiveOffer
   * @summary edit_collective_offer <PATCH>
   * @request PATCH:/collective/offers/{offer_id}
   */
  editCollectiveOffer = (
    offerId: number,
    data: PatchCollectiveOfferBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<GetCollectiveOfferResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CancelCollectiveOfferBooking
   * @summary cancel_collective_offer_booking <PATCH>
   * @request PATCH:/collective/offers/{offer_id}/cancel_booking
   */
  cancelCollectiveOfferBooking = (
    offerId: number,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers/${offerId}/cancel_booking`,
      method: 'PATCH',
      ...params,
    })
  /**
   * No description
   *
   * @name DuplicateCollectiveOffer
   * @summary duplicate_collective_offer <POST>
   * @request POST:/collective/offers/{offer_id}/duplicate
   */
  duplicateCollectiveOffer = (offerId: number, params: RequestParams = {}) =>
    this.request<GetCollectiveOfferResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}/duplicate`,
      method: 'POST',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOffersEducationalInstitution
   * @summary patch_collective_offers_educational_institution <PATCH>
   * @request PATCH:/collective/offers/{offer_id}/educational_institution
   */
  patchCollectiveOffersEducationalInstitution = (
    offerId: number,
    data: PatchCollectiveOfferEducationalInstitution,
    params: RequestParams = {}
  ) =>
    this.request<GetCollectiveOfferResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}/educational_institution`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name DeleteOfferImage
   * @summary delete_offer_image <DELETE>
   * @request DELETE:/collective/offers/{offer_id}/image
   */
  deleteOfferImage = (offerId: number, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/collective/offers/${offerId}/image`,
      method: 'DELETE',
      ...params,
    })
  /**
   * No description
   *
   * @name AttachOfferImage
   * @summary attach_offer_image <POST>
   * @request POST:/collective/offers/{offer_id}/image
   */
  attachOfferImage = (
    offerId: number,
    data: AttachImageFormModel,
    params: RequestParams = {}
  ) =>
    this.request<AttachImageResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}/image`,
      method: 'POST',
      body: data,
      type: ContentType.FormData,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchCollectiveOfferPublication
   * @summary patch_collective_offer_publication <PATCH>
   * @request PATCH:/collective/offers/{offer_id}/publish
   */
  patchCollectiveOfferPublication = (
    offerId: number,
    params: RequestParams = {}
  ) =>
    this.request<GetCollectiveOfferResponseModel, void | ValidationError>({
      path: `/collective/offers/${offerId}/publish`,
      method: 'PATCH',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name CreateCollectiveStock
   * @summary create_collective_stock <POST>
   * @request POST:/collective/stocks
   */
  createCollectiveStock = (
    data: CollectiveStockCreationBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<CollectiveStockResponseModel, void | ValidationError>({
      path: `/collective/stocks`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name EditCollectiveStock
   * @summary edit_collective_stock <PATCH>
   * @request PATCH:/collective/stocks/{collective_stock_id}
   */
  editCollectiveStock = (
    collectiveStockId: number,
    data: CollectiveStockEditionBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<CollectiveStockResponseModel, void | ValidationError>({
      path: `/collective/stocks/${collectiveStockId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
}
