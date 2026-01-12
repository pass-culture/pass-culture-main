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
  CreateOffererQueryModel,
  GetEducationalOfferersResponseModel,
  GetOffererAddressesResponseModel,
  GetOffererAddressesWithOffersOption,
  GetOffererBankAccountsResponseModel,
  GetOffererMembersResponseModel,
  GetOffererResponseModel,
  GetOffererStatsResponseModel,
  GetOfferersNamesResponseModel,
  GetOffererV2StatsResponseModel,
  HeadLineOfferResponseModel,
  InviteMemberQueryModel,
  LinkVenueToBankAccountBodyModel,
  OffererEligibilityResponseModel,
  PostOffererResponseModel,
  SaveNewOnboardingDataQueryModel,
  ValidationError,
} from './data-contracts'
import { ContentType, HttpClient, type RequestParams } from './http-client'

export class Offerers<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name CreateOfferer
   * @summary create_offerer <POST>
   * @request POST:/offerers
   */
  createOfferer = (data: CreateOffererQueryModel, params: RequestParams = {}) =>
    this.request<PostOffererResponseModel, void | ValidationError>({
      path: `/offerers`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name ListEducationalOfferers
   * @summary list_educational_offerers <GET>
   * @request GET:/offerers/educational
   */
  listEducationalOfferers = (
    query?: {
      /** Offerer Id */
      offerer_id?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<GetEducationalOfferersResponseModel, void | ValidationError>({
      path: `/offerers/educational`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name ListOfferersNames
   * @summary list_offerers_names <GET>
   * @request GET:/offerers/names
   */
  listOfferersNames = (
    query?: {
      /** Validated */
      validated?: boolean | null
      /** Validated For User */
      validated_for_user?: boolean | null
      /** Offerer Id */
      offerer_id?: number | null
    },
    params: RequestParams = {}
  ) =>
    this.request<GetOfferersNamesResponseModel, void | ValidationError>({
      path: `/offerers/names`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name SaveNewOnboardingData
   * @summary save_new_onboarding_data <POST>
   * @request POST:/offerers/new
   */
  saveNewOnboardingData = (
    data: SaveNewOnboardingDataQueryModel,
    params: RequestParams = {}
  ) =>
    this.request<PostOffererResponseModel, void | ValidationError>({
      path: `/offerers/new`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOfferer
   * @summary get_offerer <GET>
   * @request GET:/offerers/{offerer_id}
   */
  getOfferer = (offererId: number, params: RequestParams = {}) =>
    this.request<GetOffererResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererBankAccountsAndAttachedVenues
   * @summary get_offerer_bank_accounts_and_attached_venues <GET>
   * @request GET:/offerers/{offerer_id}/bank-accounts
   */
  getOffererBankAccountsAndAttachedVenues = (
    offererId: number,
    params: RequestParams = {}
  ) =>
    this.request<GetOffererBankAccountsResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/bank-accounts`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name LinkVenueToBankAccount
   * @summary link_venue_to_bank_account <PATCH>
   * @request PATCH:/offerers/{offerer_id}/bank-accounts/{bank_account_id}
   */
  linkVenueToBankAccount = (
    offererId: number,
    bankAccountId: number,
    data: LinkVenueToBankAccountBodyModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offerers/${offererId}/bank-accounts/${bankAccountId}`,
      method: 'PATCH',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererEligibility
   * @summary get_offerer_eligibility <GET>
   * @request GET:/offerers/{offerer_id}/eligibility
   */
  getOffererEligibility = (offererId: number, params: RequestParams = {}) =>
    this.request<OffererEligibilityResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/eligibility`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererHeadlineOffer
   * @summary get_offerer_headline_offer <GET>
   * @request GET:/offerers/{offerer_id}/headline-offer
   */
  getOffererHeadlineOffer = (offererId: number, params: RequestParams = {}) =>
    this.request<HeadLineOfferResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/headline-offer`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name InviteMember
   * @summary invite_member <POST>
   * @request POST:/offerers/{offerer_id}/invite
   */
  inviteMember = (
    offererId: number,
    data: InviteMemberQueryModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offerers/${offererId}/invite`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name InviteMemberAgain
   * @summary invite_member_again <POST>
   * @request POST:/offerers/{offerer_id}/invite-again
   */
  inviteMemberAgain = (
    offererId: number,
    data: InviteMemberQueryModel,
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/offerers/${offererId}/invite-again`,
      method: 'POST',
      body: data,
      type: ContentType.Json,
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererMembers
   * @summary get_offerer_members <GET>
   * @request GET:/offerers/{offerer_id}/members
   */
  getOffererMembers = (offererId: number, params: RequestParams = {}) =>
    this.request<GetOffererMembersResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/members`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererAddresses
   * @summary get_offerer_addresses <GET>
   * @request GET:/offerers/{offerer_id}/offerer_addresses
   */
  getOffererAddresses = (
    offererId: number,
    query?: {
      withOffersOption?: GetOffererAddressesWithOffersOption | null
    },
    params: RequestParams = {}
  ) =>
    this.request<GetOffererAddressesResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/offerer_addresses`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererStats
   * @summary get_offerer_stats <GET>
   * @request GET:/offerers/{offerer_id}/stats
   */
  getOffererStats = (offererId: number, params: RequestParams = {}) =>
    this.request<GetOffererStatsResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/stats`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetOffererV2Stats
   * @summary Deprecated. Please use GET /venues/<venue_id>/offers-statistics instead.
   * @request GET:/offerers/{offerer_id}/v2/stats
   * @deprecated
   */
  getOffererV2Stats = (offererId: number, params: RequestParams = {}) =>
    this.request<GetOffererV2StatsResponseModel, void | ValidationError>({
      path: `/offerers/${offererId}/v2/stats`,
      method: 'GET',
      format: 'json',
      ...params,
    })
}
