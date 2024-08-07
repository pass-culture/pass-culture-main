/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdageCulturalPartnersResponseModel } from '../models/AdageCulturalPartnersResponseModel';
import type { AttachImageFormModel } from '../models/AttachImageFormModel';
import type { AttachImageResponseModel } from '../models/AttachImageResponseModel';
import type { BookingExportType } from '../models/BookingExportType';
import type { BookingsExportStatusFilter } from '../models/BookingsExportStatusFilter';
import type { BookingStatusFilter } from '../models/BookingStatusFilter';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { ChangePasswordBodyModel } from '../models/ChangePasswordBodyModel';
import type { ChangeProEmailBody } from '../models/ChangeProEmailBody';
import type { CollectiveBookingByIdResponseModel } from '../models/CollectiveBookingByIdResponseModel';
import type { CollectiveBookingStatusFilter } from '../models/CollectiveBookingStatusFilter';
import type { CollectiveOfferDisplayedStatus } from '../models/CollectiveOfferDisplayedStatus';
import type { CollectiveOfferResponseIdModel } from '../models/CollectiveOfferResponseIdModel';
import type { CollectiveOfferTemplateBodyModel } from '../models/CollectiveOfferTemplateBodyModel';
import type { CollectiveOfferTemplateResponseIdModel } from '../models/CollectiveOfferTemplateResponseIdModel';
import type { CollectiveOfferType } from '../models/CollectiveOfferType';
import type { CollectiveStockCreationBodyModel } from '../models/CollectiveStockCreationBodyModel';
import type { CollectiveStockEditionBodyModel } from '../models/CollectiveStockEditionBodyModel';
import type { CollectiveStockResponseModel } from '../models/CollectiveStockResponseModel';
import type { CookieConsentRequest } from '../models/CookieConsentRequest';
import type { CreateOffererQueryModel } from '../models/CreateOffererQueryModel';
import type { CreateThumbnailBodyModel } from '../models/CreateThumbnailBodyModel';
import type { CreateThumbnailResponseModel } from '../models/CreateThumbnailResponseModel';
import type { DeleteFilteredStockListBody } from '../models/DeleteFilteredStockListBody';
import type { DeleteOfferRequestBody } from '../models/DeleteOfferRequestBody';
import type { DeleteStockListBody } from '../models/DeleteStockListBody';
import type { EacFormat } from '../models/EacFormat';
import type { EditVenueBodyModel } from '../models/EditVenueBodyModel';
import type { EditVenueCollectiveDataBodyModel } from '../models/EditVenueCollectiveDataBodyModel';
import type { EducationalDomainsResponseModel } from '../models/EducationalDomainsResponseModel';
import type { EducationalInstitutionsResponseModel } from '../models/EducationalInstitutionsResponseModel';
import type { EducationalRedactors } from '../models/EducationalRedactors';
import type { EventDatesInfos } from '../models/EventDatesInfos';
import type { FinanceBankAccountListResponseModel } from '../models/FinanceBankAccountListResponseModel';
import type { GenerateOffererApiKeyResponse } from '../models/GenerateOffererApiKeyResponse';
import type { GetCollectiveOfferRequestResponseModel } from '../models/GetCollectiveOfferRequestResponseModel';
import type { GetCollectiveOfferResponseModel } from '../models/GetCollectiveOfferResponseModel';
import type { GetCollectiveOfferTemplateResponseModel } from '../models/GetCollectiveOfferTemplateResponseModel';
import type { GetEducationalOfferersResponseModel } from '../models/GetEducationalOfferersResponseModel';
import type { GetIndividualOfferResponseModel } from '../models/GetIndividualOfferResponseModel';
import type { GetIndividualOfferWithAddressResponseModel } from '../models/GetIndividualOfferWithAddressResponseModel';
import type { GetMusicTypesResponse } from '../models/GetMusicTypesResponse';
import type { GetOffererAddressesResponseModel } from '../models/GetOffererAddressesResponseModel';
import type { GetOffererBankAccountsResponseModel } from '../models/GetOffererBankAccountsResponseModel';
import type { GetOffererMembersResponseModel } from '../models/GetOffererMembersResponseModel';
import type { GetOffererResponseModel } from '../models/GetOffererResponseModel';
import type { GetOfferersNamesResponseModel } from '../models/GetOfferersNamesResponseModel';
import type { GetOffererStatsResponseModel } from '../models/GetOffererStatsResponseModel';
import type { GetOffererV2StatsResponseModel } from '../models/GetOffererV2StatsResponseModel';
import type { GetStocksResponseModel } from '../models/GetStocksResponseModel';
import type { GetVenueListResponseModel } from '../models/GetVenueListResponseModel';
import type { GetVenueResponseModel } from '../models/GetVenueResponseModel';
import type { GetVenuesOfOffererFromSiretResponseModel } from '../models/GetVenuesOfOffererFromSiretResponseModel';
import type { HasInvoiceResponseModel } from '../models/HasInvoiceResponseModel';
import type { InviteMemberQueryModel } from '../models/InviteMemberQueryModel';
import type { InvoiceListV2ResponseModel } from '../models/InvoiceListV2ResponseModel';
import type { LinkVenueToBankAccountBodyModel } from '../models/LinkVenueToBankAccountBodyModel';
import type { LinkVenueToPricingPointBodyModel } from '../models/LinkVenueToPricingPointBodyModel';
import type { ListBookingsResponseModel } from '../models/ListBookingsResponseModel';
import type { ListCollectiveBookingsResponseModel } from '../models/ListCollectiveBookingsResponseModel';
import type { ListCollectiveOffersResponseModel } from '../models/ListCollectiveOffersResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { ListNationalProgramsResponseModel } from '../models/ListNationalProgramsResponseModel';
import type { ListOffersResponseModel } from '../models/ListOffersResponseModel';
import type { ListProviderResponse } from '../models/ListProviderResponse';
import type { ListVenueProviderResponse } from '../models/ListVenueProviderResponse';
import type { LoginUserBodyModel } from '../models/LoginUserBodyModel';
import type { NewPasswordBodyModel } from '../models/NewPasswordBodyModel';
import type { OffererAddressRequestModel } from '../models/OffererAddressRequestModel';
import type { OffererAddressResponseModel } from '../models/OffererAddressResponseModel';
import type { OffererStatsResponseModel } from '../models/OffererStatsResponseModel';
import type { OfferStatus } from '../models/OfferStatus';
import type { PatchAllCollectiveOffersActiveStatusBodyModel } from '../models/PatchAllCollectiveOffersActiveStatusBodyModel';
import type { PatchAllOffersActiveStatusBodyModel } from '../models/PatchAllOffersActiveStatusBodyModel';
import type { PatchCollectiveOfferActiveStatusBodyModel } from '../models/PatchCollectiveOfferActiveStatusBodyModel';
import type { PatchCollectiveOfferArchiveBodyModel } from '../models/PatchCollectiveOfferArchiveBodyModel';
import type { PatchCollectiveOfferBodyModel } from '../models/PatchCollectiveOfferBodyModel';
import type { PatchCollectiveOfferEducationalInstitution } from '../models/PatchCollectiveOfferEducationalInstitution';
import type { PatchCollectiveOfferTemplateBodyModel } from '../models/PatchCollectiveOfferTemplateBodyModel';
import type { PatchDraftOfferBodyModel } from '../models/PatchDraftOfferBodyModel';
import type { PatchDraftOfferUsefulInformationsBodyModel } from '../models/PatchDraftOfferUsefulInformationsBodyModel';
import type { PatchOfferActiveStatusBodyModel } from '../models/PatchOfferActiveStatusBodyModel';
import type { PatchOfferBodyModel } from '../models/PatchOfferBodyModel';
import type { PatchOffererAddressRequest } from '../models/PatchOffererAddressRequest';
import type { PatchOfferPublishBodyModel } from '../models/PatchOfferPublishBodyModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';
import type { PostCollectiveOfferTemplateBodyModel } from '../models/PostCollectiveOfferTemplateBodyModel';
import type { PostDraftOfferBodyModel } from '../models/PostDraftOfferBodyModel';
import type { PostOfferBodyModel } from '../models/PostOfferBodyModel';
import type { PostOffererResponseModel } from '../models/PostOffererResponseModel';
import type { PostVenueBodyModel } from '../models/PostVenueBodyModel';
import type { PostVenueProviderBody } from '../models/PostVenueProviderBody';
import type { PriceCategoryBody } from '../models/PriceCategoryBody';
import type { ProFlagsQueryModel } from '../models/ProFlagsQueryModel';
import type { ProUserCreationBodyV2Model } from '../models/ProUserCreationBodyV2Model';
import type { ResetPasswordBodyModel } from '../models/ResetPasswordBodyModel';
import type { SaveNewOnboardingDataQueryModel } from '../models/SaveNewOnboardingDataQueryModel';
import type { SharedCurrentUserResponseModel } from '../models/SharedCurrentUserResponseModel';
import type { SharedLoginUserResponseModel } from '../models/SharedLoginUserResponseModel';
import type { SirenInfo } from '../models/SirenInfo';
import type { SiretInfo } from '../models/SiretInfo';
import type { StockIdResponseModel } from '../models/StockIdResponseModel';
import type { StocksOrderedBy } from '../models/StocksOrderedBy';
import type { StocksResponseModel } from '../models/StocksResponseModel';
import type { StockStatsResponseModel } from '../models/StockStatsResponseModel';
import type { StocksUpsertBodyModel } from '../models/StocksUpsertBodyModel';
import type { SubmitReviewRequestModel } from '../models/SubmitReviewRequestModel';
import type { SuggestedSubcategoriesResponseModel } from '../models/SuggestedSubcategoriesResponseModel';
import type { UserEmailValidationResponseModel } from '../models/UserEmailValidationResponseModel';
import type { UserHasBookingResponse } from '../models/UserHasBookingResponse';
import type { UserIdentityBodyModel } from '../models/UserIdentityBodyModel';
import type { UserIdentityResponseModel } from '../models/UserIdentityResponseModel';
import type { UserPhoneBodyModel } from '../models/UserPhoneBodyModel';
import type { UserPhoneResponseModel } from '../models/UserPhoneResponseModel';
import type { UserResetEmailBodyModel } from '../models/UserResetEmailBodyModel';
import type { VenueLabelListResponseModel } from '../models/VenueLabelListResponseModel';
import type { VenueProviderResponse } from '../models/VenueProviderResponse';
import type { VenueResponseModel } from '../models/VenueResponseModel';
import type { VenuesEducationalStatusesResponseModel } from '../models/VenuesEducationalStatusesResponseModel';
import type { VenueStatsResponseModel } from '../models/VenueStatsResponseModel';
import type { VenueTypeListResponseModel } from '../models/VenueTypeListResponseModel';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DefaultService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * get_bookings_csv <GET>
   * @param page
   * @param venueId
   * @param offerId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @param offererAddressId
   * @param exportType
   * @returns any OK
   * @throws ApiError
   */
  public getBookingsCsv(
    page: number = 1,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/csv',
      query: {
        'page': page,
        'venueId': venueId,
        'offerId': offerId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
        'offererAddressId': offererAddressId,
        'exportType': exportType,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offer_price_categories_and_schedules_by_dates <GET>
   * @param offerId
   * @returns EventDatesInfos OK
   * @throws ApiError
   */
  public getOfferPriceCategoriesAndSchedulesByDates(
    offerId: number,
  ): CancelablePromise<EventDatesInfos> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/dates/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_bookings_excel <GET>
   * @param page
   * @param venueId
   * @param offerId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @param offererAddressId
   * @param exportType
   * @returns any OK
   * @throws ApiError
   */
  public getBookingsExcel(
    page: number = 1,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/excel',
      query: {
        'page': page,
        'venueId': venueId,
        'offerId': offerId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
        'offererAddressId': offererAddressId,
        'exportType': exportType,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * export_bookings_for_offer_as_csv <GET>
   * @param offerId
   * @param status
   * @param eventDate
   * @returns any OK
   * @throws ApiError
   */
  public exportBookingsForOfferAsCsv(
    offerId: number,
    status: BookingsExportStatusFilter,
    eventDate: string,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/offer/{offer_id}/csv',
      path: {
        'offer_id': offerId,
      },
      query: {
        'status': status,
        'event_date': eventDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * export_bookings_for_offer_as_excel <GET>
   * @param offerId
   * @param status
   * @param eventDate
   * @returns any OK
   * @throws ApiError
   */
  public exportBookingsForOfferAsExcel(
    offerId: number,
    status: BookingsExportStatusFilter,
    eventDate: string,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/offer/{offer_id}/excel',
      path: {
        'offer_id': offerId,
      },
      query: {
        'status': status,
        'event_date': eventDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_bookings_pro <GET>
   * @param page
   * @param venueId
   * @param offerId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @param offererAddressId
   * @param exportType
   * @returns ListBookingsResponseModel OK
   * @throws ApiError
   */
  public getBookingsPro(
    page: number = 1,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  ): CancelablePromise<ListBookingsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/pro',
      query: {
        'page': page,
        'venueId': venueId,
        'offerId': offerId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
        'offererAddressId': offererAddressId,
        'exportType': exportType,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_user_has_bookings <GET>
   * @returns UserHasBookingResponse OK
   * @throws ApiError
   */
  public getUserHasBookings(): CancelablePromise<UserHasBookingResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/pro/userHasBookings',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_bookings_csv <GET>
   * @param page
   * @param venueId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveBookingsCsv(
    page: number = 1,
    venueId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: CollectiveBookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookings/csv',
      query: {
        'page': page,
        'venueId': venueId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_bookings_excel <GET>
   * @param page
   * @param venueId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveBookingsExcel(
    page: number = 1,
    venueId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: CollectiveBookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookings/excel',
      query: {
        'page': page,
        'venueId': venueId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_bookings_pro <GET>
   * @param page
   * @param venueId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @returns ListCollectiveBookingsResponseModel OK
   * @throws ApiError
   */
  public getCollectiveBookingsPro(
    page: number = 1,
    venueId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: CollectiveBookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
  ): CancelablePromise<ListCollectiveBookingsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookings/pro',
      query: {
        'page': page,
        'venueId': venueId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_user_has_collective_bookings <GET>
   * @returns UserHasBookingResponse OK
   * @throws ApiError
   */
  public getUserHasCollectiveBookings(): CancelablePromise<UserHasBookingResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookings/pro/userHasBookings',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_booking_by_id <GET>
   * @param bookingId
   * @returns CollectiveBookingByIdResponseModel OK
   * @throws ApiError
   */
  public getCollectiveBookingById(
    bookingId: number,
  ): CancelablePromise<CollectiveBookingByIdResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookings/{booking_id}',
      path: {
        'booking_id': bookingId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_educational_domains <GET>
   * @returns EducationalDomainsResponseModel OK
   * @throws ApiError
   */
  public listEducationalDomains(): CancelablePromise<EducationalDomainsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/educational-domains',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_offers <GET>
   * @param nameOrIsbn
   * @param offererId
   * @param status
   * @param venueId
   * @param categoryId
   * @param creationMode
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param collectiveOfferType
   * @param format
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffers(
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: (Array<CollectiveOfferDisplayedStatus> | CollectiveOfferDisplayedStatus) | null,
    venueId?: number | null,
    categoryId?: string | null,
    creationMode?: string | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    collectiveOfferType?: CollectiveOfferType | null,
    format?: EacFormat | null,
  ): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers',
      query: {
        'nameOrIsbn': nameOrIsbn,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'categoryId': categoryId,
        'creationMode': creationMode,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'collectiveOfferType': collectiveOfferType,
        'format': format,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_collective_offer <POST>
   * @param requestBody
   * @returns CollectiveOfferResponseIdModel Created
   * @throws ApiError
   */
  public createCollectiveOffer(
    requestBody?: PostCollectiveOfferBodyModel,
  ): CancelablePromise<CollectiveOfferResponseIdModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_collective_offer_template <POST>
   * @param requestBody
   * @returns CollectiveOfferResponseIdModel Created
   * @throws ApiError
   */
  public createCollectiveOfferTemplate(
    requestBody?: PostCollectiveOfferTemplateBodyModel,
  ): CancelablePromise<CollectiveOfferResponseIdModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers-template',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offers_template_active_status <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersTemplateActiveStatus(
    requestBody?: PatchCollectiveOfferActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offers_template_archive <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersTemplateArchive(
    requestBody?: PatchCollectiveOfferArchiveBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/archive',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_offer_request <GET>
   * @param requestId
   * @returns GetCollectiveOfferRequestResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferRequest(
    requestId: number,
  ): CancelablePromise<GetCollectiveOfferRequestResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers-template/request/{request_id}',
      path: {
        'request_id': requestId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_offer_template <GET>
   * @param offerId
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplate(
    offerId: number,
  ): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers-template/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * edit_collective_offer_template <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public editCollectiveOfferTemplate(
    offerId: number,
    requestBody?: PatchCollectiveOfferTemplateBodyModel,
  ): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_collective_offer_template_from_collective_offer <POST>
   * @param offerId
   * @param requestBody
   * @returns CollectiveOfferTemplateResponseIdModel Created
   * @throws ApiError
   */
  public createCollectiveOfferTemplateFromCollectiveOffer(
    offerId: number,
    requestBody?: CollectiveOfferTemplateBodyModel,
  ): CancelablePromise<CollectiveOfferTemplateResponseIdModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers-template/{offer_id}/',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_offer_template_image <DELETE>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public deleteOfferTemplateImage(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/collective/offers-template/{offer_id}/image',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * attach_offer_template_image <POST>
   * @param offerId
   * @param formData
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferTemplateImage(
    offerId: number,
    formData?: AttachImageFormModel,
  ): CancelablePromise<AttachImageResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers-template/{offer_id}/image',
      path: {
        'offer_id': offerId,
      },
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offer_template_publication <PATCH>
   * @param offerId
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferTemplatePublication(
    offerId: number,
  ): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/{offer_id}/publish',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offers_active_status <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersActiveStatus(
    requestBody?: PatchCollectiveOfferActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_all_collective_offers_active_status <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchAllCollectiveOffersActiveStatus(
    requestBody?: PatchAllCollectiveOffersActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/all-active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offers_archive <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersArchive(
    requestBody?: PatchCollectiveOfferArchiveBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/archive',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_autocomplete_educational_redactors_for_uai <GET>
   * @param uai
   * @param candidate
   * @returns EducationalRedactors OK
   * @throws ApiError
   */
  public getAutocompleteEducationalRedactorsForUai(
    uai: string,
    candidate: string,
  ): CancelablePromise<EducationalRedactors> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/redactors',
      query: {
        'uai': uai,
        'candidate': candidate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_collective_offer <GET>
   * @param offerId
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffer(
    offerId: number,
  ): CancelablePromise<GetCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * edit_collective_offer <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public editCollectiveOffer(
    offerId: number,
    requestBody?: PatchCollectiveOfferBodyModel,
  ): CancelablePromise<GetCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * cancel_collective_offer_booking <PATCH>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public cancelCollectiveOfferBooking(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/{offer_id}/cancel_booking',
      path: {
        'offer_id': offerId,
      },
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * duplicate_collective_offer <POST>
   * @param offerId
   * @returns GetCollectiveOfferResponseModel Created
   * @throws ApiError
   */
  public duplicateCollectiveOffer(
    offerId: number,
  ): CancelablePromise<GetCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers/{offer_id}/duplicate',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offers_educational_institution <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOffersEducationalInstitution(
    offerId: number,
    requestBody?: PatchCollectiveOfferEducationalInstitution,
  ): CancelablePromise<GetCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/{offer_id}/educational_institution',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_offer_image <DELETE>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public deleteOfferImage(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/collective/offers/{offer_id}/image',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * attach_offer_image <POST>
   * @param offerId
   * @param formData
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferImage(
    offerId: number,
    formData?: AttachImageFormModel,
  ): CancelablePromise<AttachImageResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers/{offer_id}/image',
      path: {
        'offer_id': offerId,
      },
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_collective_offer_publication <PATCH>
   * @param offerId
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferPublication(
    offerId: number,
  ): CancelablePromise<GetCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/{offer_id}/publish',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_collective_stock <POST>
   * @param requestBody
   * @returns CollectiveStockResponseModel Created
   * @throws ApiError
   */
  public createCollectiveStock(
    requestBody?: CollectiveStockCreationBodyModel,
  ): CancelablePromise<CollectiveStockResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/stocks',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * edit_collective_stock <PATCH>
   * @param collectiveStockId
   * @param requestBody
   * @returns CollectiveStockResponseModel OK
   * @throws ApiError
   */
  public editCollectiveStock(
    collectiveStockId: number,
    requestBody?: CollectiveStockEditionBodyModel,
  ): CancelablePromise<CollectiveStockResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/stocks/{collective_stock_id}',
      path: {
        'collective_stock_id': collectiveStockId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        401: `Unauthorized`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_educational_partners <GET>
   * @returns AdageCulturalPartnersResponseModel OK
   * @throws ApiError
   */
  public getEducationalPartners(): CancelablePromise<AdageCulturalPartnersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/cultural-partners',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_educational_institutions <GET>
   * @param perPageLimit
   * @param page
   * @returns EducationalInstitutionsResponseModel OK
   * @throws ApiError
   */
  public getEducationalInstitutions(
    perPageLimit: number = 1000,
    page: number = 1,
  ): CancelablePromise<EducationalInstitutionsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/educational_institutions',
      query: {
        'perPageLimit': perPageLimit,
        'page': page,
      },
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_features <GET>
   * @returns ListFeatureResponseModel OK
   * @throws ApiError
   */
  public listFeatures(): CancelablePromise<ListFeatureResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/features',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_bank_accounts <GET>
   * @returns FinanceBankAccountListResponseModel OK
   * @throws ApiError
   */
  public getBankAccounts(): CancelablePromise<FinanceBankAccountListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/bank-accounts',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_combined_invoices <GET>
   * @param invoiceReferences
   * @returns any OK
   * @throws ApiError
   */
  public getCombinedInvoices(
    invoiceReferences: Array<string>,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/combined-invoices',
      query: {
        'invoiceReferences': invoiceReferences,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_national_programs <GET>
   * @returns ListNationalProgramsResponseModel OK
   * @throws ApiError
   */
  public getNationalPrograms(): CancelablePromise<ListNationalProgramsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/national-programs',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_offerer <POST>
   * @param requestBody
   * @returns PostOffererResponseModel Created
   * @throws ApiError
   */
  public createOfferer(
    requestBody?: CreateOffererQueryModel,
  ): CancelablePromise<PostOffererResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_api_key <DELETE>
   * @param apiKeyPrefix
   * @returns void
   * @throws ApiError
   */
  public deleteApiKey(
    apiKeyPrefix: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/offerers/api_keys/{api_key_prefix}',
      path: {
        'api_key_prefix': apiKeyPrefix,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_educational_offerers <GET>
   * @param offererId
   * @returns GetEducationalOfferersResponseModel OK
   * @throws ApiError
   */
  public listEducationalOfferers(
    offererId?: number | null,
  ): CancelablePromise<GetEducationalOfferersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/educational',
      query: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_offerers_names <GET>
   * @param validated
   * @param validatedForUser
   * @param offererId
   * @returns GetOfferersNamesResponseModel OK
   * @throws ApiError
   */
  public listOfferersNames(
    validated?: boolean | null,
    validatedForUser?: boolean | null,
    offererId?: number | null,
  ): CancelablePromise<GetOfferersNamesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/names',
      query: {
        'validated': validated,
        'validated_for_user': validatedForUser,
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * save_new_onboarding_data <POST>
   * @param requestBody
   * @returns PostOffererResponseModel Created
   * @throws ApiError
   */
  public saveNewOnboardingData(
    requestBody?: SaveNewOnboardingDataQueryModel,
  ): CancelablePromise<PostOffererResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/new',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer <GET>
   * @param offererId
   * @returns GetOffererResponseModel OK
   * @throws ApiError
   */
  public getOfferer(
    offererId: number,
  ): CancelablePromise<GetOffererResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_offerer_address <PATCH>
   * @param offererId
   * @param offererAddressId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchOffererAddress(
    offererId: number,
    offererAddressId: number,
    requestBody?: PatchOffererAddressRequest,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offerers/{offerer_id}/address/{offerer_address_id}',
      path: {
        'offerer_id': offererId,
        'offerer_address_id': offererAddressId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_addresses <GET>
   * @param offererId
   * @param onlyWithOffers
   * @returns GetOffererAddressesResponseModel OK
   * @throws ApiError
   */
  public getOffererAddresses(
    offererId: number,
    onlyWithOffers: boolean = false,
  ): CancelablePromise<GetOffererAddressesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/addresses',
      path: {
        'offerer_id': offererId,
      },
      query: {
        'onlyWithOffers': onlyWithOffers,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_offerer_address <POST>
   * @param offererId
   * @param requestBody
   * @returns OffererAddressResponseModel Created
   * @throws ApiError
   */
  public createOffererAddress(
    offererId: number,
    requestBody?: OffererAddressRequestModel,
  ): CancelablePromise<OffererAddressResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/{offerer_id}/addresses',
      path: {
        'offerer_id': offererId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * generate_api_key_route <POST>
   * @param offererId
   * @returns GenerateOffererApiKeyResponse OK
   * @throws ApiError
   */
  public generateApiKeyRoute(
    offererId: number,
  ): CancelablePromise<GenerateOffererApiKeyResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/{offerer_id}/api_keys',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_bank_accounts_and_attached_venues <GET>
   * @param offererId
   * @returns GetOffererBankAccountsResponseModel OK
   * @throws ApiError
   */
  public getOffererBankAccountsAndAttachedVenues(
    offererId: number,
  ): CancelablePromise<GetOffererBankAccountsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/bank-accounts',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * link_venue_to_bank_account <PATCH>
   * @param offererId
   * @param bankAccountId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public linkVenueToBankAccount(
    offererId: number,
    bankAccountId: number,
    requestBody?: LinkVenueToBankAccountBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offerers/{offerer_id}/bank-accounts/{bank_account_id}',
      path: {
        'offerer_id': offererId,
        'bank_account_id': bankAccountId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_stats_dashboard_url <GET>
   * @param offererId
   * @returns OffererStatsResponseModel OK
   * @throws ApiError
   */
  public getOffererStatsDashboardUrl(
    offererId: number,
  ): CancelablePromise<OffererStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/dashboard',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * invite_member <POST>
   * @param offererId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public inviteMember(
    offererId: number,
    requestBody?: InviteMemberQueryModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/{offerer_id}/invite',
      path: {
        'offerer_id': offererId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_members <GET>
   * @param offererId
   * @returns GetOffererMembersResponseModel OK
   * @throws ApiError
   */
  public getOffererMembers(
    offererId: number,
  ): CancelablePromise<GetOffererMembersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/members',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_stats <GET>
   * @param offererId
   * @returns GetOffererStatsResponseModel OK
   * @throws ApiError
   */
  public getOffererStats(
    offererId: number,
  ): CancelablePromise<GetOffererStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/stats',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offerer_v2_stats <GET>
   * @param offererId
   * @returns GetOffererV2StatsResponseModel OK
   * @throws ApiError
   */
  public getOffererV2Stats(
    offererId: number,
  ): CancelablePromise<GetOffererV2StatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/v2/stats',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_offers <GET>
   * @param nameOrIsbn
   * @param offererId
   * @param status
   * @param venueId
   * @param categoryId
   * @param creationMode
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param collectiveOfferType
   * @param offererAddressId
   * @returns ListOffersResponseModel OK
   * @throws ApiError
   */
  public listOffers(
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: (OfferStatus | CollectiveOfferDisplayedStatus) | null,
    venueId?: number | null,
    categoryId?: string | null,
    creationMode?: string | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    collectiveOfferType?: CollectiveOfferType | null,
    offererAddressId?: number | null,
  ): CancelablePromise<ListOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers',
      query: {
        'nameOrIsbn': nameOrIsbn,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'categoryId': categoryId,
        'creationMode': creationMode,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'collectiveOfferType': collectiveOfferType,
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_offer <POST>
   * @param requestBody
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public postOffer(
    requestBody?: PostOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_offers_active_status <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchOffersActiveStatus(
    requestBody?: PatchOfferActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_all_offers_active_status <PATCH>
   * @param requestBody
   * @returns any Accepted
   * @throws ApiError
   */
  public patchAllOffersActiveStatus(
    requestBody?: PatchAllOffersActiveStatusBodyModel,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/all-active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_categories <GET>
   * @returns CategoriesResponseModel OK
   * @throws ApiError
   */
  public getCategories(): CancelablePromise<CategoriesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/categories',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_draft_offers <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public deleteDraftOffers(
    requestBody?: DeleteOfferRequestBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/delete-draft',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_draft_offer <POST>
   * @param requestBody
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public postDraftOffer(
    requestBody?: PostDraftOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/draft',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_draft_offer <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public patchDraftOffer(
    offerId: number,
    requestBody?: PatchDraftOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/draft/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_draft_offer_useful_informations <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public patchDraftOfferUsefulInformations(
    offerId: number,
    requestBody?: PatchDraftOfferUsefulInformationsBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/draft/{offer_id}/useful-informations',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_music_types <GET>
   * @returns GetMusicTypesResponse OK
   * @throws ApiError
   */
  public getMusicTypes(): CancelablePromise<GetMusicTypesResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/music-types',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_publish_offer <PATCH>
   * @param requestBody
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public patchPublishOffer(
    requestBody?: PatchOfferPublishBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/publish',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_suggested_subcategories <GET>
   * @param offerName
   * @param offerDescription
   * @param venueId
   * @returns SuggestedSubcategoriesResponseModel OK
   * @throws ApiError
   */
  public getSuggestedSubcategories(
    offerName: string,
    offerDescription?: string | null,
    venueId?: number | null,
  ): CancelablePromise<SuggestedSubcategoriesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/suggested-subcategories',
      query: {
        'offer_name': offerName,
        'offer_description': offerDescription,
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_thumbnail <POST>
   * @param formData
   * @returns CreateThumbnailResponseModel Created
   * @throws ApiError
   */
  public createThumbnail(
    formData?: CreateThumbnailBodyModel,
  ): CancelablePromise<CreateThumbnailResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/thumbnails/',
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_thumbnail <DELETE>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public deleteThumbnail(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/offers/thumbnails/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_offer <GET>
   * @param offerId
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public getOffer(
    offerId: number,
  ): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_offer <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public patchOffer(
    offerId: number,
    requestBody?: PatchOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_price_categories <POST>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public postPriceCategories(
    offerId: number,
    requestBody?: PriceCategoryBody,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/{offer_id}/price_categories',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_price_category <DELETE>
   * @param offerId
   * @param priceCategoryId
   * @returns void
   * @throws ApiError
   */
  public deletePriceCategory(
    offerId: number,
    priceCategoryId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/offers/{offer_id}/price_categories/{price_category_id}',
      path: {
        'offer_id': offerId,
        'price_category_id': priceCategoryId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_stocks_stats <GET>
   * @param offerId
   * @returns StockStatsResponseModel OK
   * @throws ApiError
   */
  public getStocksStats(
    offerId: number,
  ): CancelablePromise<StockStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{offer_id}/stocks-stats',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_stocks <GET>
   * @param offerId
   * @param date
   * @param time
   * @param priceCategoryId
   * @param orderBy
   * @param orderByDesc
   * @param page
   * @param stocksLimitPerPage
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public getStocks(
    offerId: number,
    date?: string | null,
    time?: string | null,
    priceCategoryId?: number | null,
    orderBy?: StocksOrderedBy,
    orderByDesc: boolean = false,
    page: number = 1,
    stocksLimitPerPage: number = 20,
  ): CancelablePromise<GetStocksResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{offer_id}/stocks/',
      path: {
        'offer_id': offerId,
      },
      query: {
        'date': date,
        'time': time,
        'price_category_id': priceCategoryId,
        'order_by': orderBy,
        'order_by_desc': orderByDesc,
        'page': page,
        'stocks_limit_per_page': stocksLimitPerPage,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_all_filtered_stocks <POST>
   * @param offerId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public deleteAllFilteredStocks(
    offerId: number,
    requestBody?: DeleteFilteredStockListBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/{offer_id}/stocks/all-delete',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_stocks <POST>
   * @param offerId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public deleteStocks(
    offerId: number,
    requestBody?: DeleteStockListBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/{offer_id}/stocks/delete',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_reimbursements_csv <GET>
   * @param offererId
   * @param bankAccountId
   * @param reimbursementPeriodBeginningDate
   * @param reimbursementPeriodEndingDate
   * @returns any OK
   * @throws ApiError
   */
  public getReimbursementsCsv(
    offererId: number,
    bankAccountId?: number,
    reimbursementPeriodBeginningDate?: string,
    reimbursementPeriodEndingDate?: string,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/reimbursements/csv',
      query: {
        'offererId': offererId,
        'bankAccountId': bankAccountId,
        'reimbursementPeriodBeginningDate': reimbursementPeriodBeginningDate,
        'reimbursementPeriodEndingDate': reimbursementPeriodEndingDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_siren_info <GET>
   * @param siren
   * @returns SirenInfo OK
   * @throws ApiError
   */
  public getSirenInfo(
    siren: string,
  ): CancelablePromise<SirenInfo> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/sirene/siren/{siren}',
      path: {
        'siren': siren,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_siret_info <GET>
   * @param siret
   * @returns SiretInfo OK
   * @throws ApiError
   */
  public getSiretInfo(
    siret: string,
  ): CancelablePromise<SiretInfo> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/sirene/siret/{siret}',
      path: {
        'siret': siret,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * upsert_stocks <POST>
   * @param requestBody
   * @returns StocksResponseModel Created
   * @throws ApiError
   */
  public upsertStocks(
    requestBody?: StocksUpsertBodyModel,
  ): CancelablePromise<StocksResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/stocks/bulk',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_stock <DELETE>
   * @param stockId
   * @returns StockIdResponseModel OK
   * @throws ApiError
   */
  public deleteStock(
    stockId: number,
  ): CancelablePromise<StockIdResponseModel> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/stocks/{stock_id}',
      path: {
        'stock_id': stockId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * connect_as <GET>
   * @param token
   * @returns any OK
   * @throws ApiError
   */
  public connectAs(
    token: string,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/connect-as/{token}',
      path: {
        'token': token,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * cookies_consent <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public cookiesConsent(
    requestBody?: CookieConsentRequest,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/cookies',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_profile <GET>
   * @returns SharedCurrentUserResponseModel OK
   * @throws ApiError
   */
  public getProfile(): CancelablePromise<SharedCurrentUserResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/current',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_user_email <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public postUserEmail(
    requestBody?: UserResetEmailBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_user_email_pending_validation <GET>
   * @returns UserEmailValidationResponseModel OK
   * @throws ApiError
   */
  public getUserEmailPendingValidation(): CancelablePromise<UserEmailValidationResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/email_pending_validation',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_user_identity <PATCH>
   * @param requestBody
   * @returns UserIdentityResponseModel OK
   * @throws ApiError
   */
  public patchUserIdentity(
    requestBody?: UserIdentityBodyModel,
  ): CancelablePromise<UserIdentityResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/identity',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * submit_new_nav_review <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public submitNewNavReview(
    requestBody?: SubmitReviewRequestModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/log-new-nav-review',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_new_password <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public postNewPassword(
    requestBody?: NewPasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/new-password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_new_pro_nav <POST>
   * @returns void
   * @throws ApiError
   */
  public postNewProNav(): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/new-pro-nav',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_change_password <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public postChangePassword(
    requestBody?: ChangePasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_user_phone <PATCH>
   * @param requestBody
   * @returns UserPhoneResponseModel OK
   * @throws ApiError
   */
  public patchUserPhone(
    requestBody?: UserPhoneBodyModel,
  ): CancelablePromise<UserPhoneResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/phone',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_pro_flags <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public postProFlags(
    requestBody?: ProFlagsQueryModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/pro_flags',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * reset_password <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public resetPassword(
    requestBody?: ResetPasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/reset-password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_pro_user_rgs_seen <PATCH>
   * @returns void
   * @throws ApiError
   */
  public patchProUserRgsSeen(): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/rgs-seen',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * signin <POST>
   * @param requestBody
   * @returns SharedLoginUserResponseModel OK
   * @throws ApiError
   */
  public signin(
    requestBody?: LoginUserBodyModel,
  ): CancelablePromise<SharedLoginUserResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/signin',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * signout <GET>
   * @returns void
   * @throws ApiError
   */
  public signout(): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/signout',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * check_activation_token_exists <GET>
   * @param token
   * @returns void
   * @throws ApiError
   */
  public checkActivationTokenExists(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_user_tuto_seen <PATCH>
   * @returns void
   * @throws ApiError
   */
  public patchUserTutoSeen(): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/tuto-seen',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * patch_validate_email <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchValidateEmail(
    requestBody?: ChangeProEmailBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/validate_email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * has_invoice <GET>
   * @param offererId
   * @returns HasInvoiceResponseModel OK
   * @throws ApiError
   */
  public hasInvoice(
    offererId: number,
  ): CancelablePromise<HasInvoiceResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/finance/has-invoice',
      query: {
        'offererId': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_invoices_v2 <GET>
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param bankAccountId
   * @param offererId
   * @returns InvoiceListV2ResponseModel OK
   * @throws ApiError
   */
  public getInvoicesV2(
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    bankAccountId?: number | null,
    offererId?: number | null,
  ): CancelablePromise<InvoiceListV2ResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/finance/invoices',
      query: {
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'bankAccountId': bankAccountId,
        'offererId': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_reimbursements_csv_v2 <GET>
   * @param invoicesReferences
   * @returns any OK
   * @throws ApiError
   */
  public getReimbursementsCsvV2(
    invoicesReferences: Array<string>,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/reimbursements/csv',
      query: {
        'invoicesReferences': invoicesReferences,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * signup_pro_V2 <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public signupProV2(
    requestBody?: ProUserCreationBodyV2Model,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/v2/users/signup/pro',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * validate_user <PATCH>
   * @param token
   * @returns void
   * @throws ApiError
   */
  public validateUser(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/validate/user/{token}',
      path: {
        'token': token,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * fetch_venue_labels <GET>
   * @returns VenueLabelListResponseModel OK
   * @throws ApiError
   */
  public fetchVenueLabels(): CancelablePromise<VenueLabelListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venue-labels',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venue_types <GET>
   * @returns VenueTypeListResponseModel OK
   * @throws ApiError
   */
  public getVenueTypes(): CancelablePromise<VenueTypeListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venue-types',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * list_venue_providers <GET>
   * @param venueId
   * @returns ListVenueProviderResponse OK
   * @throws ApiError
   */
  public listVenueProviders(
    venueId: number,
  ): CancelablePromise<ListVenueProviderResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venueProviders',
      query: {
        'venueId': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * create_venue_provider <POST>
   * @param requestBody
   * @returns VenueProviderResponse Created
   * @throws ApiError
   */
  public createVenueProvider(
    requestBody?: PostVenueProviderBody,
  ): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/venueProviders',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * update_venue_provider <PUT>
   * @param requestBody
   * @returns VenueProviderResponse OK
   * @throws ApiError
   */
  public updateVenueProvider(
    requestBody?: PostVenueProviderBody,
  ): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/venueProviders',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_providers_by_venue <GET>
   * @param venueId
   * @returns ListProviderResponse OK
   * @throws ApiError
   */
  public getProvidersByVenue(
    venueId: number,
  ): CancelablePromise<ListProviderResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venueProviders/{venue_id}',
      path: {
        'venue_id': venueId,
      },
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_venue_provider <DELETE>
   * @param venueProviderId
   * @returns void
   * @throws ApiError
   */
  public deleteVenueProvider(
    venueProviderId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/venueProviders/{venue_provider_id}',
      path: {
        'venue_provider_id': venueProviderId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venues <GET>
   * @param validated
   * @param activeOfferersOnly
   * @param offererId
   * @returns GetVenueListResponseModel OK
   * @throws ApiError
   */
  public getVenues(
    validated?: boolean | null,
    activeOfferersOnly?: boolean | null,
    offererId?: number | null,
  ): CancelablePromise<GetVenueListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues',
      query: {
        'validated': validated,
        'activeOfferersOnly': activeOfferersOnly,
        'offererId': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * post_create_venue <POST>
   * @param requestBody
   * @returns VenueResponseModel Created
   * @throws ApiError
   */
  public postCreateVenue(
    requestBody?: PostVenueBodyModel,
  ): CancelablePromise<VenueResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/venues',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venues_educational_statuses <GET>
   * @returns VenuesEducationalStatusesResponseModel OK
   * @throws ApiError
   */
  public getVenuesEducationalStatuses(): CancelablePromise<VenuesEducationalStatusesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues-educational-statuses',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venues_of_offerer_from_siret <GET>
   * @param siret
   * @returns GetVenuesOfOffererFromSiretResponseModel OK
   * @throws ApiError
   */
  public getVenuesOfOffererFromSiret(
    siret: string,
  ): CancelablePromise<GetVenuesOfOffererFromSiretResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/siret/{siret}',
      path: {
        'siret': siret,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venue <GET>
   * @param venueId
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public getVenue(
    venueId: number,
  ): CancelablePromise<GetVenueResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{venue_id}',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * edit_venue <PATCH>
   * @param venueId
   * @param requestBody
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public editVenue(
    venueId: number,
    requestBody?: EditVenueBodyModel,
  ): CancelablePromise<GetVenueResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/venues/{venue_id}',
      path: {
        'venue_id': venueId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * delete_venue_banner <DELETE>
   * @param venueId
   * @returns void
   * @throws ApiError
   */
  public deleteVenueBanner(
    venueId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/venues/{venue_id}/banner',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * edit_venue_collective_data <PATCH>
   * @param venueId
   * @param requestBody
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public editVenueCollectiveData(
    venueId: number,
    requestBody?: EditVenueCollectiveDataBodyModel,
  ): CancelablePromise<GetVenueResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/venues/{venue_id}/collective-data',
      path: {
        'venue_id': venueId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venue_stats_dashboard_url <GET>
   * @param venueId
   * @returns OffererStatsResponseModel OK
   * @throws ApiError
   */
  public getVenueStatsDashboardUrl(
    venueId: number,
  ): CancelablePromise<OffererStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{venue_id}/dashboard',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * link_venue_to_pricing_point <POST>
   * @param venueId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public linkVenueToPricingPoint(
    venueId: number,
    requestBody?: LinkVenueToPricingPointBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/venues/{venue_id}/pricing-point',
      path: {
        'venue_id': venueId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * get_venue_stats <GET>
   * @param venueId
   * @returns VenueStatsResponseModel OK
   * @throws ApiError
   */
  public getVenueStats(
    venueId: number,
  ): CancelablePromise<VenueStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{venue_id}/stats',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }
}
