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
  BookingExportType,
  BookingStatusFilter,
  BookingsExportStatusFilter,
  EventDatesInfos,
  GetBookingResponse,
  ListBookingsResponseModel,
  UserHasBookingResponse,
  ValidationError,
} from './data-contracts'
import { HttpClient, type RequestParams } from './http-client'

export class Bookings<
  SecurityDataType = unknown,
> extends HttpClient<SecurityDataType> {
  /**
   * No description
   *
   * @name GetBookingsCsv
   * @summary get_bookings_csv <GET>
   * @request GET:/bookings/csv
   */
  getBookingsCsv = (
    query?: {
      /**
       * Page
       * @default 1
       */
      page?: number
      /**
       * Offererid
       * @default null
       */
      offererId?: number | null
      /**
       * Venueid
       * @default null
       */
      venueId?: number | null
      /**
       * Offerid
       * @default null
       */
      offerId?: number | null
      /**
       * Eventdate
       * @default null
       */
      eventDate?: string | null
      /** @default null */
      bookingStatusFilter?: BookingStatusFilter | null
      /**
       * Bookingperiodbeginningdate
       * @default null
       */
      bookingPeriodBeginningDate?: string | null
      /**
       * Bookingperiodendingdate
       * @default null
       */
      bookingPeriodEndingDate?: string | null
      /**
       * Offereraddressid
       * @default null
       */
      offererAddressId?: number | null
      /** @default null */
      exportType?: BookingExportType | null
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/csv`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name GetOfferPriceCategoriesAndSchedulesByDates
   * @summary get_offer_price_categories_and_schedules_by_dates <GET>
   * @request GET:/bookings/dates/{offer_id}
   */
  getOfferPriceCategoriesAndSchedulesByDates = (
    offerId: number,
    params: RequestParams = {}
  ) =>
    this.request<EventDatesInfos, void | ValidationError>({
      path: `/bookings/dates/${offerId}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetBookingsExcel
   * @summary get_bookings_excel <GET>
   * @request GET:/bookings/excel
   */
  getBookingsExcel = (
    query?: {
      /**
       * Page
       * @default 1
       */
      page?: number
      /**
       * Offererid
       * @default null
       */
      offererId?: number | null
      /**
       * Venueid
       * @default null
       */
      venueId?: number | null
      /**
       * Offerid
       * @default null
       */
      offerId?: number | null
      /**
       * Eventdate
       * @default null
       */
      eventDate?: string | null
      /** @default null */
      bookingStatusFilter?: BookingStatusFilter | null
      /**
       * Bookingperiodbeginningdate
       * @default null
       */
      bookingPeriodBeginningDate?: string | null
      /**
       * Bookingperiodendingdate
       * @default null
       */
      bookingPeriodEndingDate?: string | null
      /**
       * Offereraddressid
       * @default null
       */
      offererAddressId?: number | null
      /** @default null */
      exportType?: BookingExportType | null
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/excel`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name PatchBookingKeepByToken
   * @summary patch_booking_keep_by_token <PATCH>
   * @request PATCH:/bookings/keep/token/{token}
   */
  patchBookingKeepByToken = (token: string, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/keep/token/${token}`,
      method: 'PATCH',
      ...params,
    })
  /**
   * No description
   *
   * @name ExportBookingsForOfferAsCsv
   * @summary export_bookings_for_offer_as_csv <GET>
   * @request GET:/bookings/offer/{offer_id}/csv
   */
  exportBookingsForOfferAsCsv = (
    offerId: number,
    query: {
      status: BookingsExportStatusFilter
      /**
       * Eventdate
       * @format date
       */
      eventDate: string
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/offer/${offerId}/csv`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name ExportBookingsForOfferAsExcel
   * @summary export_bookings_for_offer_as_excel <GET>
   * @request GET:/bookings/offer/{offer_id}/excel
   */
  exportBookingsForOfferAsExcel = (
    offerId: number,
    query: {
      status: BookingsExportStatusFilter
      /**
       * Eventdate
       * @format date
       */
      eventDate: string
    },
    params: RequestParams = {}
  ) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/offer/${offerId}/excel`,
      method: 'GET',
      query: query,
      ...params,
    })
  /**
   * No description
   *
   * @name GetBookingsPro
   * @summary get_bookings_pro <GET>
   * @request GET:/bookings/pro
   */
  getBookingsPro = (
    query?: {
      /**
       * Page
       * @default 1
       */
      page?: number
      /**
       * Offererid
       * @default null
       */
      offererId?: number | null
      /**
       * Venueid
       * @default null
       */
      venueId?: number | null
      /**
       * Offerid
       * @default null
       */
      offerId?: number | null
      /**
       * Eventdate
       * @default null
       */
      eventDate?: string | null
      /** @default null */
      bookingStatusFilter?: BookingStatusFilter | null
      /**
       * Bookingperiodbeginningdate
       * @default null
       */
      bookingPeriodBeginningDate?: string | null
      /**
       * Bookingperiodendingdate
       * @default null
       */
      bookingPeriodEndingDate?: string | null
      /**
       * Offereraddressid
       * @default null
       */
      offererAddressId?: number | null
      /** @default null */
      exportType?: BookingExportType | null
    },
    params: RequestParams = {}
  ) =>
    this.request<ListBookingsResponseModel, void | ValidationError>({
      path: `/bookings/pro`,
      method: 'GET',
      query: query,
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetUserHasBookings
   * @summary get_user_has_bookings <GET>
   * @request GET:/bookings/pro/userHasBookings
   */
  getUserHasBookings = (params: RequestParams = {}) =>
    this.request<UserHasBookingResponse, void | ValidationError>({
      path: `/bookings/pro/userHasBookings`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name GetBookingByToken
   * @summary get_booking_by_token <GET>
   * @request GET:/bookings/token/{token}
   */
  getBookingByToken = (token: string, params: RequestParams = {}) =>
    this.request<GetBookingResponse, void | ValidationError>({
      path: `/bookings/token/${token}`,
      method: 'GET',
      format: 'json',
      ...params,
    })
  /**
   * No description
   *
   * @name PatchBookingUseByToken
   * @summary patch_booking_use_by_token <PATCH>
   * @request PATCH:/bookings/use/token/{token}
   */
  patchBookingUseByToken = (token: string, params: RequestParams = {}) =>
    this.request<void, void | ValidationError>({
      path: `/bookings/use/token/${token}`,
      method: 'PATCH',
      ...params,
    })
}
