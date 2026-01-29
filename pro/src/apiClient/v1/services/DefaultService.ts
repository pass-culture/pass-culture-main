/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ArtistsResponseModel } from '../models/ArtistsResponseModel';
import type { AttachImageFormModel } from '../models/AttachImageFormModel';
import type { AttachImageResponseModel } from '../models/AttachImageResponseModel';
import type { BookingExportType } from '../models/BookingExportType';
import type { BookingsExportStatusFilter } from '../models/BookingsExportStatusFilter';
import type { BookingStatusFilter } from '../models/BookingStatusFilter';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { ChangePasswordBodyModel } from '../models/ChangePasswordBodyModel';
import type { ChangeProEmailBody } from '../models/ChangeProEmailBody';
import type { CheckTokenBodyModel } from '../models/CheckTokenBodyModel';
import type { CollectiveLocationType } from '../models/CollectiveLocationType';
import type { CollectiveOfferDisplayedStatus } from '../models/CollectiveOfferDisplayedStatus';
import type { CollectiveOfferResponseIdModel } from '../models/CollectiveOfferResponseIdModel';
import type { CollectiveStockCreationBodyModel } from '../models/CollectiveStockCreationBodyModel';
import type { CollectiveStockEditionBodyModel } from '../models/CollectiveStockEditionBodyModel';
import type { CollectiveStockResponseModel } from '../models/CollectiveStockResponseModel';
import type { CookieConsentRequest } from '../models/CookieConsentRequest';
import type { CreateOffererQueryModel } from '../models/CreateOffererQueryModel';
import type { CreateOfferHighlightRequestBodyModel } from '../models/CreateOfferHighlightRequestBodyModel';
import type { CreateThumbnailBodyModel } from '../models/CreateThumbnailBodyModel';
import type { CreateThumbnailResponseModel } from '../models/CreateThumbnailResponseModel';
import type { DeleteOfferRequestBody } from '../models/DeleteOfferRequestBody';
import type { DeleteStockListBody } from '../models/DeleteStockListBody';
import type { EacFormat } from '../models/EacFormat';
import type { EditVenueBodyModel } from '../models/EditVenueBodyModel';
import type { EditVenueCollectiveDataBodyModel } from '../models/EditVenueCollectiveDataBodyModel';
import type { EducationalDomainsResponseModel } from '../models/EducationalDomainsResponseModel';
import type { EducationalInstitutionsResponseModel } from '../models/EducationalInstitutionsResponseModel';
import type { EducationalRedactors } from '../models/EducationalRedactors';
import type { EventDatesInfos } from '../models/EventDatesInfos';
import type { EventStocksBulkCreateBodyModel } from '../models/EventStocksBulkCreateBodyModel';
import type { EventStocksBulkUpdateBodyModel } from '../models/EventStocksBulkUpdateBodyModel';
import type { FinanceBankAccountListResponseModel } from '../models/FinanceBankAccountListResponseModel';
import type { GetActiveEANOfferResponseModel } from '../models/GetActiveEANOfferResponseModel';
import type { GetBookingResponse } from '../models/GetBookingResponse';
import type { GetCollectiveOfferRequestResponseModel } from '../models/GetCollectiveOfferRequestResponseModel';
import type { GetCollectiveOfferResponseModel } from '../models/GetCollectiveOfferResponseModel';
import type { GetCollectiveOfferTemplateResponseModel } from '../models/GetCollectiveOfferTemplateResponseModel';
import type { GetEducationalOfferersResponseModel } from '../models/GetEducationalOfferersResponseModel';
import type { GetIndividualOfferResponseModel } from '../models/GetIndividualOfferResponseModel';
import type { GetIndividualOfferWithAddressResponseModel } from '../models/GetIndividualOfferWithAddressResponseModel';
import type { GetMusicTypesResponse } from '../models/GetMusicTypesResponse';
import type { GetOffererAddressesResponseModel } from '../models/GetOffererAddressesResponseModel';
import type { GetOffererAddressesWithOffersOption } from '../models/GetOffererAddressesWithOffersOption';
import type { GetOffererBankAccountsResponseModel } from '../models/GetOffererBankAccountsResponseModel';
import type { GetOffererMembersResponseModel } from '../models/GetOffererMembersResponseModel';
import type { GetOffererResponseModel } from '../models/GetOffererResponseModel';
import type { GetOfferersNamesResponseModel } from '../models/GetOfferersNamesResponseModel';
import type { GetOffererStatsResponseModel } from '../models/GetOffererStatsResponseModel';
import type { GetOffererV2StatsResponseModel } from '../models/GetOffererV2StatsResponseModel';
import type { GetOffersStatsResponseModel } from '../models/GetOffersStatsResponseModel';
import type { GetProductInformations } from '../models/GetProductInformations';
import type { GetStocksResponseModel } from '../models/GetStocksResponseModel';
import type { GetVenueListLiteResponseModel } from '../models/GetVenueListLiteResponseModel';
import type { GetVenueListResponseModel } from '../models/GetVenueListResponseModel';
import type { GetVenueOffersStatsModel } from '../models/GetVenueOffersStatsModel';
import type { GetVenueResponseModel } from '../models/GetVenueResponseModel';
import type { GetVenuesOfOffererFromSiretResponseModel } from '../models/GetVenuesOfOffererFromSiretResponseModel';
import type { HasInvoiceResponseModel } from '../models/HasInvoiceResponseModel';
import type { HeadlineOfferCreationBodyModel } from '../models/HeadlineOfferCreationBodyModel';
import type { HeadlineOfferDeleteBodyModel } from '../models/HeadlineOfferDeleteBodyModel';
import type { HeadLineOfferResponseModel } from '../models/HeadLineOfferResponseModel';
import type { HighlightsResponseModel } from '../models/HighlightsResponseModel';
import type { InviteMemberQueryModel } from '../models/InviteMemberQueryModel';
import type { InvoiceListV2ResponseModel } from '../models/InvoiceListV2ResponseModel';
import type { LinkVenueToBankAccountBodyModel } from '../models/LinkVenueToBankAccountBodyModel';
import type { LinkVenueToPricingPointBodyModel } from '../models/LinkVenueToPricingPointBodyModel';
import type { ListBookingsResponseModel } from '../models/ListBookingsResponseModel';
import type { ListCollectiveOffersResponseModel } from '../models/ListCollectiveOffersResponseModel';
import type { ListCollectiveOfferTemplatesResponseModel } from '../models/ListCollectiveOfferTemplatesResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { ListOffersResponseModel } from '../models/ListOffersResponseModel';
import type { ListProviderResponse } from '../models/ListProviderResponse';
import type { ListVenueProviderResponse } from '../models/ListVenueProviderResponse';
import type { LoginUserBodyModel } from '../models/LoginUserBodyModel';
import type { MinimalPostOfferBodyModel } from '../models/MinimalPostOfferBodyModel';
import type { NewPasswordBodyModel } from '../models/NewPasswordBodyModel';
import type { OffererEligibilityResponseModel } from '../models/OffererEligibilityResponseModel';
import type { OfferOpeningHoursSchema } from '../models/OfferOpeningHoursSchema';
import type { OfferStatus } from '../models/OfferStatus';
import type { PatchAllOffersActiveStatusBodyModel } from '../models/PatchAllOffersActiveStatusBodyModel';
import type { PatchCollectiveOfferActiveStatusBodyModel } from '../models/PatchCollectiveOfferActiveStatusBodyModel';
import type { PatchCollectiveOfferArchiveBodyModel } from '../models/PatchCollectiveOfferArchiveBodyModel';
import type { PatchCollectiveOfferBodyModel } from '../models/PatchCollectiveOfferBodyModel';
import type { PatchCollectiveOfferEducationalInstitution } from '../models/PatchCollectiveOfferEducationalInstitution';
import type { PatchCollectiveOfferTemplateBodyModel } from '../models/PatchCollectiveOfferTemplateBodyModel';
import type { PatchOfferActiveStatusBodyModel } from '../models/PatchOfferActiveStatusBodyModel';
import type { PatchOfferBodyModel } from '../models/PatchOfferBodyModel';
import type { PatchOfferPublishBodyModel } from '../models/PatchOfferPublishBodyModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';
import type { PostCollectiveOfferTemplateBodyModel } from '../models/PostCollectiveOfferTemplateBodyModel';
import type { PostOfferBodyModel } from '../models/PostOfferBodyModel';
import type { PostOffererResponseModel } from '../models/PostOffererResponseModel';
import type { PostVenueProviderBody } from '../models/PostVenueProviderBody';
import type { PriceCategoryBody } from '../models/PriceCategoryBody';
import type { ProAnonymizationEligibilityResponseModel } from '../models/ProAnonymizationEligibilityResponseModel';
import type { ProUserCreationBodyV2Model } from '../models/ProUserCreationBodyV2Model';
import type { PutVenueProviderBody } from '../models/PutVenueProviderBody';
import type { ResetPasswordBodyModel } from '../models/ResetPasswordBodyModel';
import type { SaveNewOnboardingDataQueryModel } from '../models/SaveNewOnboardingDataQueryModel';
import type { SharedCurrentUserResponseModel } from '../models/SharedCurrentUserResponseModel';
import type { SharedLoginUserResponseModel } from '../models/SharedLoginUserResponseModel';
import type { StatisticsModel } from '../models/StatisticsModel';
import type { StocksOrderedBy } from '../models/StocksOrderedBy';
import type { StockStatsResponseModel } from '../models/StockStatsResponseModel';
import type { StructureDataBodyModel } from '../models/StructureDataBodyModel';
import type { SubmitReviewRequestModel } from '../models/SubmitReviewRequestModel';
import type { ThingStocksBulkUpsertBodyModel } from '../models/ThingStocksBulkUpsertBodyModel';
import type { UserEmailValidationResponseModel } from '../models/UserEmailValidationResponseModel';
import type { UserHasBookingResponse } from '../models/UserHasBookingResponse';
import type { UserIdentityBodyModel } from '../models/UserIdentityBodyModel';
import type { UserIdentityResponseModel } from '../models/UserIdentityResponseModel';
import type { UserPhoneBodyModel } from '../models/UserPhoneBodyModel';
import type { UserPhoneResponseModel } from '../models/UserPhoneResponseModel';
import type { UserResetEmailBodyModel } from '../models/UserResetEmailBodyModel';
import type { VenueLabelListResponseModel } from '../models/VenueLabelListResponseModel';
import type { VenueProviderResponse } from '../models/VenueProviderResponse';
import type { VenuesEducationalStatusesResponseModel } from '../models/VenuesEducationalStatusesResponseModel';
import type { VenueTypeListResponseModel } from '../models/VenueTypeListResponseModel';
import type { VideoData } from '../models/VideoData';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DefaultService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * get_artists <GET>
   * @param search
   * @returns ArtistsResponseModel OK
   * @throws ApiError
   */
  public getArtists(
    search: string,
  ): CancelablePromise<ArtistsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/artists',
      query: {
        'search': search,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_bookings_csv <GET>
   * @param page
   * @param offererId
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
    offererId?: (number | null),
    venueId?: (number | null),
    offerId?: (number | null),
    eventDate?: (string | null),
    bookingStatusFilter?: (BookingStatusFilter | null),
    bookingPeriodBeginningDate?: (string | null),
    bookingPeriodEndingDate?: (string | null),
    offererAddressId?: (number | null),
    exportType?: (BookingExportType | null),
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/csv',
      query: {
        'page': page,
        'offererId': offererId,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_bookings_excel <GET>
   * @param page
   * @param offererId
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
    offererId?: (number | null),
    venueId?: (number | null),
    offerId?: (number | null),
    eventDate?: (string | null),
    bookingStatusFilter?: (BookingStatusFilter | null),
    bookingPeriodBeginningDate?: (string | null),
    bookingPeriodEndingDate?: (string | null),
    offererAddressId?: (number | null),
    exportType?: (BookingExportType | null),
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/excel',
      query: {
        'page': page,
        'offererId': offererId,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * patch_booking_keep_by_token <PATCH>
   * @param token
   * @returns void
   * @throws ApiError
   */
  public patchBookingKeepByToken(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/bookings/keep/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        404: `La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder.`,
        410: `La requête est refusée car la contremarque n'a pas encore été validée, a été annulée, ou son remboursement a été initié`,
        422: `Unprocessable Content`,
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
        'eventDate': eventDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        'eventDate': eventDate,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_bookings_pro <GET>
   * @param page
   * @param offererId
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
    offererId?: (number | null),
    venueId?: (number | null),
    offerId?: (number | null),
    eventDate?: (string | null),
    bookingStatusFilter?: (BookingStatusFilter | null),
    bookingPeriodBeginningDate?: (string | null),
    bookingPeriodEndingDate?: (string | null),
    offererAddressId?: (number | null),
    exportType?: (BookingExportType | null),
  ): CancelablePromise<ListBookingsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/pro',
      query: {
        'page': page,
        'offererId': offererId,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_booking_by_token <GET>
   * @param token
   * @returns GetBookingResponse La contremarque existe et n’est pas validée
   * @throws ApiError
   */
  public getBookingByToken(
    token: string,
  ): CancelablePromise<GetBookingResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        404: `La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder.`,
        410: `Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * patch_booking_use_by_token <PATCH>
   * @param token
   * @returns void
   * @throws ApiError
   */
  public patchBookingUseByToken(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/bookings/use/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        404: `La contremarque n'existe pas, ou vous n'avez pas les droits nécessaires pour y accéder.`,
        410: `Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offers <GET>
   * @param name
   * @param offererId
   * @param status
   * @param venueId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param format
   * @param locationType
   * @param offererAddressId
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffers(
    name?: (string | null),
    offererId?: (number | null),
    status?: (Array<CollectiveOfferDisplayedStatus> | null),
    venueId?: (number | null),
    periodBeginningDate?: (string | null),
    periodEndingDate?: (string | null),
    format?: (EacFormat | null),
    locationType?: (CollectiveLocationType | null),
    offererAddressId?: (number | null),
  ): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookable-offers',
      query: {
        'name': name,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'format': format,
        'locationType': locationType,
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PostCollectiveOfferBodyModel,
  ): CancelablePromise<CollectiveOfferResponseIdModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offer_templates <GET>
   * @param name
   * @param offererId
   * @param status
   * @param venueId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param format
   * @param locationType
   * @param offererAddressId
   * @returns ListCollectiveOfferTemplatesResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplates(
    name?: (string | null),
    offererId?: (number | null),
    status?: (Array<CollectiveOfferDisplayedStatus> | null),
    venueId?: (number | null),
    periodBeginningDate?: (string | null),
    periodEndingDate?: (string | null),
    format?: (EacFormat | null),
    locationType?: (CollectiveLocationType | null),
    offererAddressId?: (number | null),
  ): CancelablePromise<ListCollectiveOfferTemplatesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers-template',
      query: {
        'name': name,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'format': format,
        'locationType': locationType,
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: PostCollectiveOfferTemplateBodyModel,
  ): CancelablePromise<CollectiveOfferResponseIdModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/offers-template',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferArchiveBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/archive',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferTemplateBodyModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    formData: AttachImageFormModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferArchiveBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers/archive',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offers_csv <GET>
   * @param name
   * @param offererId
   * @param status
   * @param venueId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param format
   * @param locationType
   * @param offererAddressId
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveOffersCsv(
    name?: (string | null),
    offererId?: (number | null),
    status?: (Array<CollectiveOfferDisplayedStatus> | null),
    venueId?: (number | null),
    periodBeginningDate?: (string | null),
    periodEndingDate?: (string | null),
    format?: (EacFormat | null),
    locationType?: (CollectiveLocationType | null),
    offererAddressId?: (number | null),
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/csv',
      query: {
        'name': name,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'format': format,
        'locationType': locationType,
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offers_excel <GET>
   * @param name
   * @param offererId
   * @param status
   * @param venueId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param format
   * @param locationType
   * @param offererAddressId
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveOffersExcel(
    name?: (string | null),
    offererId?: (number | null),
    status?: (Array<CollectiveOfferDisplayedStatus> | null),
    venueId?: (number | null),
    periodBeginningDate?: (string | null),
    periodEndingDate?: (string | null),
    format?: (EacFormat | null),
    locationType?: (CollectiveLocationType | null),
    offererAddressId?: (number | null),
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/excel',
      query: {
        'name': name,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'format': format,
        'locationType': locationType,
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferBodyModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PatchCollectiveOfferEducationalInstitution,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    formData: AttachImageFormModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: CollectiveStockCreationBodyModel,
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
        422: `Unprocessable Content`,
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
    requestBody: CollectiveStockEditionBodyModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offer_video_metadata <GET>
   * @param videoUrl
   * @returns VideoData OK
   * @throws ApiError
   */
  public getOfferVideoMetadata(
    videoUrl: string,
  ): CancelablePromise<VideoData> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/get-offer-video-data',
      query: {
        'videoUrl': videoUrl,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_statistics <GET>
   * @param venueIds
   * @returns StatisticsModel OK
   * @throws ApiError
   */
  public getStatistics(
    venueIds?: Array<number>,
  ): CancelablePromise<StatisticsModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/get-statistics',
      query: {
        'venueIds': venueIds,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_product_by_ean <GET>
   * @param ean
   * @param offererId
   * @returns GetProductInformations OK
   * @throws ApiError
   */
  public getProductByEan(
    ean: string,
    offererId: number,
  ): CancelablePromise<GetProductInformations> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/get_product_by_ean/{ean}/{offerer_id}',
      path: {
        'ean': ean,
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_highlights <GET>
   * @returns HighlightsResponseModel OK
   * @throws ApiError
   */
  public getHighlights(): CancelablePromise<HighlightsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/highlights',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_venues_lite <GET>
   * @param validated
   * @param activeOfferersOnly
   * @param offererId
   * @returns GetVenueListLiteResponseModel OK
   * @throws ApiError
   */
  public getVenuesLite(
    validated?: boolean | null,
    activeOfferersOnly?: boolean | null,
    offererId?: number | null,
  ): CancelablePromise<GetVenueListLiteResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/lite/venues',
      query: {
        'validated': validated,
        'activeOfferersOnly': activeOfferersOnly,
        'offererId': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: CreateOffererQueryModel,
  ): CancelablePromise<PostOffererResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: SaveNewOnboardingDataQueryModel,
  ): CancelablePromise<PostOffererResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/new',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: LinkVenueToBankAccountBodyModel,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offerer_eligibility <GET>
   * @param offererId
   * @returns OffererEligibilityResponseModel OK
   * @throws ApiError
   */
  public getOffererEligibility(
    offererId: number,
  ): CancelablePromise<OffererEligibilityResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/eligibility',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offerer_headline_offer <GET>
   * @param offererId
   * @returns HeadLineOfferResponseModel OK
   * @throws ApiError
   */
  public getOffererHeadlineOffer(
    offererId: number,
  ): CancelablePromise<HeadLineOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/headline-offer',
      path: {
        'offerer_id': offererId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: InviteMemberQueryModel,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * invite_member_again <POST>
   * @param offererId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public inviteMemberAgain(
    offererId: number,
    requestBody: InviteMemberQueryModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offerers/{offerer_id}/invite-again',
      path: {
        'offerer_id': offererId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offerer_addresses <GET>
   * @param offererId
   * @param withOffersOption
   * @returns GetOffererAddressesResponseModel OK
   * @throws ApiError
   */
  public getOffererAddresses(
    offererId: number,
    withOffersOption?: GetOffererAddressesWithOffersOption | null,
  ): CancelablePromise<GetOffererAddressesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/offerer_addresses',
      path: {
        'offerer_id': offererId,
      },
      query: {
        'withOffersOption': withOffersOption,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * @deprecated
   * Deprecated. Please use GET /venues/<venue_id>/offers-statistics instead.
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
        422: `Unprocessable Content`,
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
        'offererAddressId': offererAddressId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: MinimalPostOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: PatchOfferActiveStatusBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: PatchAllOffersActiveStatusBodyModel,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/all-active-status',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: DeleteOfferRequestBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/delete-draft',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * delete_headline_offer <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public deleteHeadlineOffer(
    requestBody: HeadlineOfferDeleteBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/delete_headline',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: PatchOfferPublishBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/publish',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
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
    formData: CreateThumbnailBodyModel,
  ): CancelablePromise<CreateThumbnailResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/thumbnails',
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * upsert_headline_offer <POST>
   * @param requestBody
   * @returns HeadLineOfferResponseModel Created
   * @throws ApiError
   */
  public upsertHeadlineOffer(
    requestBody: HeadlineOfferCreationBodyModel,
  ): CancelablePromise<HeadLineOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/upsert_headline',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * patch_offer <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public patchOffer(
    offerId: number,
    requestBody: PatchOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * post_highlight_request_offer <POST>
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferWithAddressResponseModel Created
   * @throws ApiError
   */
  public postHighlightRequestOffer(
    offerId: number,
    requestBody: CreateOfferHighlightRequestBodyModel,
  ): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/{offer_id}/highlight-requests',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offer_opening_hours <GET>
   * @param offerId
   * @returns OfferOpeningHoursSchema OK
   * @throws ApiError
   */
  public getOfferOpeningHours(
    offerId: number,
  ): CancelablePromise<OfferOpeningHoursSchema> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{offer_id}/opening-hours',
      path: {
        'offer_id': offerId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * Create or update an offer's opening hours (erase existing if any)
   * For each day of the week, there can be at most two pairs of timespans (opening hours start and end).
   *
   * Week days might have null/empty opening hours: in that case, no data will be inserted. This allows a more flexible way to send data.
   *
   * The output data will always contain every week day. If no opening hours has been set, the timespan data will be null.
   *
   * Note: since opening hours should always be erased before any new data is inserted, this route can also be used as a DELETE one.
   * @param offerId
   * @param requestBody
   * @returns OfferOpeningHoursSchema OK
   * @throws ApiError
   */
  public upsertOfferOpeningHours(
    offerId: number,
    requestBody: OfferOpeningHoursSchema,
  ): CancelablePromise<OfferOpeningHoursSchema> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/{offer_id}/opening-hours',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * Replace all price categories of an offer.
   * - If a price category exists in the DB but not in `price_categories`, it is deleted. - Otherwise, price categories are updated or created as needed.
   * @param offerId
   * @param requestBody
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public replaceOfferPriceCategories(
    offerId: number,
    requestBody: PriceCategoryBody,
  ): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/offers/{offer_id}/price_categories',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * Upsert all price categories stocks of a non-event offer.
   * - If a stock exists in the DB but not in `stocks`, it is soft-deleted. - Otherwise, stocks are updated or created as needed.
   * @param offerId
   * @param requestBody
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public upsertOfferStocks(
    offerId: number,
    requestBody: ThingStocksBulkUpsertBodyModel,
  ): CancelablePromise<GetStocksResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/offers/{offer_id}/stocks/',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * delete_stocks <POST>
   * @param offerId
   * @param requestBody
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public deleteStocks(
    offerId: number,
    requestBody: DeleteStockListBody,
  ): CancelablePromise<GetStocksResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_active_venue_offer_by_ean <GET>
   * @param venueId
   * @param ean
   * @returns GetActiveEANOfferResponseModel OK
   * @throws ApiError
   */
  public getActiveVenueOfferByEan(
    venueId: number,
    ean: string,
  ): CancelablePromise<GetActiveEANOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{venue_id}/ean/{ean}',
      path: {
        'venue_id': venueId,
        'ean': ean,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * bulk_update_event_stocks <PATCH>
   * @param requestBody
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public bulkUpdateEventStocks(
    requestBody: EventStocksBulkUpdateBodyModel,
  ): CancelablePromise<GetStocksResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/stocks/bulk',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * bulk_create_event_stocks <POST>
   * @param requestBody
   * @returns GetStocksResponseModel Created
   * @throws ApiError
   */
  public bulkCreateEventStocks(
    requestBody: EventStocksBulkCreateBodyModel,
  ): CancelablePromise<GetStocksResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/stocks/bulk',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_structure_data <GET>
   * @param searchInput
   * @returns StructureDataBodyModel OK
   * @throws ApiError
   */
  public getStructureData(
    searchInput: string,
  ): CancelablePromise<StructureDataBodyModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/structure/search/{search_input}',
      path: {
        'search_input': searchInput,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * anonymize <POST>
   * @returns void
   * @throws ApiError
   */
  public anonymize(): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/anonymize',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_pro_anonymization_eligibility <GET>
   * @returns ProAnonymizationEligibilityResponseModel OK
   * @throws ApiError
   */
  public getProAnonymizationEligibility(): CancelablePromise<ProAnonymizationEligibilityResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/users/anonymize/eligibility',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * post_check_token <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public postCheckToken(
    requestBody: CheckTokenBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/check-token',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: CookieConsentRequest,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/cookies',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: UserResetEmailBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: UserIdentityBodyModel,
  ): CancelablePromise<UserIdentityResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/identity',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * submit_user_review <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public submitUserReview(
    requestBody: SubmitReviewRequestModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/log-user-review',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: NewPasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/new-password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: ChangePasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: UserPhoneBodyModel,
  ): CancelablePromise<UserPhoneResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/phone',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: ResetPasswordBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/reset-password',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: LoginUserBodyModel,
  ): CancelablePromise<SharedLoginUserResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/signin',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * signup_pro <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public signupPro(
    requestBody: ProUserCreationBodyV2Model,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/signup',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: ChangeProEmailBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/validate_email',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
      url: '/users/validate_signup/{token}',
      path: {
        'token': token,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    periodBeginningDate?: (string | null),
    periodEndingDate?: (string | null),
    bankAccountId?: (number | null),
    offererId?: (number | null),
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * create_offer <POST>
   * @param requestBody
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public createOffer(
    requestBody: PostOfferBodyModel,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/v2/offers',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
      url: '/venue-providers/{venue_provider_id}',
      path: {
        'venue_provider_id': venueProviderId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * update_venue_provider <PUT>
   * @param venueProviderId
   * @param requestBody
   * @returns VenueProviderResponse OK
   * @throws ApiError
   */
  public updateVenueProvider(
    venueProviderId: number,
    requestBody: PutVenueProviderBody,
  ): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/venue-providers/{venue_provider_id}',
      path: {
        'venue_provider_id': venueProviderId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_offers_statistics <GET>
   * @param venueId
   * @returns GetOffersStatsResponseModel OK
   * @throws ApiError
   */
  public getOffersStatistics(
    venueId: number,
  ): CancelablePromise<GetOffersStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venue/{venue_id}/offers-statistics',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * @deprecated
   * [deprecated] please use /lite/venues instead
   * This route loads way too much data.
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: EditVenueBodyModel,
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
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
    requestBody: EditVenueCollectiveDataBodyModel,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_venue_offers_stats <GET>
   * @param venueId
   * @returns GetVenueOffersStatsModel OK
   * @throws ApiError
   */
  public getVenueOffersStats(
    venueId: number,
  ): CancelablePromise<GetVenueOffersStatsModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{venue_id}/offers-statistics',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
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
    requestBody: LinkVenueToPricingPointBodyModel,
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
        422: `Unprocessable Content`,
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
      url: '/venues/{venue_id}/providers',
      path: {
        'venue_id': venueId,
      },
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
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
      url: '/venues/{venue_id}/venue-providers',
      path: {
        'venue_id': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * create_venue_provider <POST>
   * @param venueId
   * @param requestBody
   * @returns VenueProviderResponse Created
   * @throws ApiError
   */
  public createVenueProvider(
    venueId: number,
    requestBody: PostVenueProviderBody,
  ): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/venues/{venue_id}/venue-providers',
      path: {
        'venue_id': venueId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
}
