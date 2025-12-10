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
import type { CheckTokenBodyModel } from '../models/CheckTokenBodyModel';
import type { CollectiveLocationType } from '../models/CollectiveLocationType';
import type { CollectiveOfferDisplayedStatus } from '../models/CollectiveOfferDisplayedStatus';
import type { CollectiveOfferResponseIdModel } from '../models/CollectiveOfferResponseIdModel';
import type { CollectiveOfferType } from '../models/CollectiveOfferType';
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
import type { PatchDraftOfferBodyModel } from '../models/PatchDraftOfferBodyModel';
import type { PatchOfferActiveStatusBodyModel } from '../models/PatchOfferActiveStatusBodyModel';
import type { PatchOfferBodyModel } from '../models/PatchOfferBodyModel';
import type { PatchOfferPublishBodyModel } from '../models/PatchOfferPublishBodyModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';
import type { PostCollectiveOfferTemplateBodyModel } from '../models/PostCollectiveOfferTemplateBodyModel';
import type { PostDraftOfferBodyModel } from '../models/PostDraftOfferBodyModel';
import type { PostOfferBodyModel } from '../models/PostOfferBodyModel';
import type { PostOffererResponseModel } from '../models/PostOffererResponseModel';
import type { PostVenueProviderBody } from '../models/PostVenueProviderBody';
import type { PriceCategoryBody } from '../models/PriceCategoryBody';
import type { ProUserCreationBodyV2Model } from '../models/ProUserCreationBodyV2Model';
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
   * get_bookings_csv <GET>
   * @returns any OK
   * @throws ApiError
   */
  public getBookingsCsv({
    page = 1,
    offererId,
    venueId,
    offerId,
    eventDate,
    bookingStatusFilter,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    offererAddressId,
    exportType,
  }: {
    page?: number,
    offererId?: number | null,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  }): CancelablePromise<any> {
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
   * @returns EventDatesInfos OK
   * @throws ApiError
   */
  public getOfferPriceCategoriesAndSchedulesByDates({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<EventDatesInfos> {
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
   * @returns any OK
   * @throws ApiError
   */
  public getBookingsExcel({
    page = 1,
    offererId,
    venueId,
    offerId,
    eventDate,
    bookingStatusFilter,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    offererAddressId,
    exportType,
  }: {
    page?: number,
    offererId?: number | null,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  }): CancelablePromise<any> {
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
   * @returns void
   * @throws ApiError
   */
  public patchBookingKeepByToken({
    token,
  }: {
    token: string,
  }): CancelablePromise<void> {
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
   * @returns any OK
   * @throws ApiError
   */
  public exportBookingsForOfferAsCsv({
    offerId,
    status,
    eventDate,
  }: {
    offerId: number,
    status: BookingsExportStatusFilter,
    eventDate: string,
  }): CancelablePromise<any> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * export_bookings_for_offer_as_excel <GET>
   * @returns any OK
   * @throws ApiError
   */
  public exportBookingsForOfferAsExcel({
    offerId,
    status,
    eventDate,
  }: {
    offerId: number,
    status: BookingsExportStatusFilter,
    eventDate: string,
  }): CancelablePromise<any> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_bookings_pro <GET>
   * @returns ListBookingsResponseModel OK
   * @throws ApiError
   */
  public getBookingsPro({
    page = 1,
    offererId,
    venueId,
    offerId,
    eventDate,
    bookingStatusFilter,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    offererAddressId,
    exportType,
  }: {
    page?: number,
    offererId?: number | null,
    venueId?: number | null,
    offerId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offererAddressId?: number | null,
    exportType?: BookingExportType | null,
  }): CancelablePromise<ListBookingsResponseModel> {
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
   * @returns GetBookingResponse La contremarque existe et n’est pas validée
   * @throws ApiError
   */
  public getBookingByToken({
    token,
  }: {
    token: string,
  }): CancelablePromise<GetBookingResponse> {
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
   * @returns void
   * @throws ApiError
   */
  public patchBookingUseByToken({
    token,
  }: {
    token: string,
  }): CancelablePromise<void> {
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
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffers({
    nameOrIsbn,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    format,
    locationType,
    offererAddressId,
  }: {
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: Array<CollectiveOfferDisplayedStatus> | null,
    venueId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    format?: EacFormat | null,
    locationType?: CollectiveLocationType | null,
    offererAddressId?: number | null,
  }): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/bookable-offers',
      query: {
        'nameOrIsbn': nameOrIsbn,
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
   * @returns CollectiveOfferResponseIdModel Created
   * @throws ApiError
   */
  public createCollectiveOffer({
    requestBody,
  }: {
    requestBody: PostCollectiveOfferBodyModel,
  }): CancelablePromise<CollectiveOfferResponseIdModel> {
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
   * @returns ListCollectiveOfferTemplatesResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplates({
    nameOrIsbn,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    format,
    locationType,
    offererAddressId,
  }: {
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: Array<CollectiveOfferDisplayedStatus> | null,
    venueId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    format?: EacFormat | null,
    locationType?: CollectiveLocationType | null,
    offererAddressId?: number | null,
  }): CancelablePromise<ListCollectiveOfferTemplatesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers-template',
      query: {
        'nameOrIsbn': nameOrIsbn,
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
   * @returns CollectiveOfferResponseIdModel Created
   * @throws ApiError
   */
  public createCollectiveOfferTemplate({
    requestBody,
  }: {
    requestBody: PostCollectiveOfferTemplateBodyModel,
  }): CancelablePromise<CollectiveOfferResponseIdModel> {
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
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersTemplateActiveStatus({
    requestBody,
  }: {
    requestBody: PatchCollectiveOfferActiveStatusBodyModel,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersTemplateArchive({
    requestBody,
  }: {
    requestBody: PatchCollectiveOfferArchiveBodyModel,
  }): CancelablePromise<void> {
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
   * @returns GetCollectiveOfferRequestResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferRequest({
    requestId,
  }: {
    requestId: number,
  }): CancelablePromise<GetCollectiveOfferRequestResponseModel> {
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
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplate({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
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
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public editCollectiveOfferTemplate({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchCollectiveOfferTemplateBodyModel,
  }): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public deleteOfferTemplateImage({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<void> {
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
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferTemplateImage({
    offerId,
    formData,
  }: {
    offerId: number,
    formData: AttachImageFormModel,
  }): CancelablePromise<AttachImageResponseModel> {
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
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferTemplatePublication({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetCollectiveOfferTemplateResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public patchCollectiveOffersArchive({
    requestBody,
  }: {
    requestBody: PatchCollectiveOfferArchiveBodyModel,
  }): CancelablePromise<void> {
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
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveOffersCsv({
    nameOrIsbn,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    format,
    locationType,
    offererAddressId,
  }: {
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: Array<CollectiveOfferDisplayedStatus> | null,
    venueId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    format?: EacFormat | null,
    locationType?: CollectiveLocationType | null,
    offererAddressId?: number | null,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/csv',
      query: {
        'nameOrIsbn': nameOrIsbn,
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
   * @returns any OK
   * @throws ApiError
   */
  public getCollectiveOffersExcel({
    nameOrIsbn,
    offererId,
    status,
    venueId,
    periodBeginningDate,
    periodEndingDate,
    format,
    locationType,
    offererAddressId,
  }: {
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: Array<CollectiveOfferDisplayedStatus> | null,
    venueId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    format?: EacFormat | null,
    locationType?: CollectiveLocationType | null,
    offererAddressId?: number | null,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/excel',
      query: {
        'nameOrIsbn': nameOrIsbn,
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
   * @returns EducationalRedactors OK
   * @throws ApiError
   */
  public getAutocompleteEducationalRedactorsForUai({
    uai,
    candidate,
  }: {
    uai: string,
    candidate: string,
  }): CancelablePromise<EducationalRedactors> {
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
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffer({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetCollectiveOfferResponseModel> {
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
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public editCollectiveOffer({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchCollectiveOfferBodyModel,
  }): CancelablePromise<GetCollectiveOfferResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public cancelCollectiveOfferBooking({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<void> {
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
   * @returns GetCollectiveOfferResponseModel Created
   * @throws ApiError
   */
  public duplicateCollectiveOffer({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetCollectiveOfferResponseModel> {
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
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOffersEducationalInstitution({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchCollectiveOfferEducationalInstitution,
  }): CancelablePromise<GetCollectiveOfferResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public deleteOfferImage({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<void> {
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
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferImage({
    offerId,
    formData,
  }: {
    offerId: number,
    formData: AttachImageFormModel,
  }): CancelablePromise<AttachImageResponseModel> {
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
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferPublication({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetCollectiveOfferResponseModel> {
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
   * @returns CollectiveStockResponseModel Created
   * @throws ApiError
   */
  public createCollectiveStock({
    requestBody,
  }: {
    requestBody: CollectiveStockCreationBodyModel,
  }): CancelablePromise<CollectiveStockResponseModel> {
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
   * @returns CollectiveStockResponseModel OK
   * @throws ApiError
   */
  public editCollectiveStock({
    collectiveStockId,
    requestBody,
  }: {
    collectiveStockId: number,
    requestBody: CollectiveStockEditionBodyModel,
  }): CancelablePromise<CollectiveStockResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_educational_institutions <GET>
   * @returns EducationalInstitutionsResponseModel OK
   * @throws ApiError
   */
  public getEducationalInstitutions({
    perPageLimit = 1000,
    page = 1,
  }: {
    perPageLimit?: number,
    page?: number,
  }): CancelablePromise<EducationalInstitutionsResponseModel> {
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
   * @returns any OK
   * @throws ApiError
   */
  public getCombinedInvoices({
    invoiceReferences,
  }: {
    invoiceReferences: Array<string>,
  }): CancelablePromise<any> {
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
   * @returns VideoData OK
   * @throws ApiError
   */
  public getOfferVideoMetadata({
    videoUrl,
  }: {
    videoUrl: string,
  }): CancelablePromise<VideoData> {
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
   * @returns StatisticsModel OK
   * @throws ApiError
   */
  public getStatistics({
    venueIds,
  }: {
    venueIds?: Array<number>,
  }): CancelablePromise<StatisticsModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/get-statistics',
      query: {
        'venue_ids': venueIds,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_product_by_ean <GET>
   * @returns GetProductInformations OK
   * @throws ApiError
   */
  public getProductByEan({
    ean,
    offererId,
  }: {
    ean: string,
    offererId: number,
  }): CancelablePromise<GetProductInformations> {
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
   * @returns GetVenueListLiteResponseModel OK
   * @throws ApiError
   */
  public getVenuesLite({
    validated,
    activeOfferersOnly,
    offererId,
  }: {
    validated?: boolean | null,
    activeOfferersOnly?: boolean | null,
    offererId?: number | null,
  }): CancelablePromise<GetVenueListLiteResponseModel> {
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
   * @returns PostOffererResponseModel Created
   * @throws ApiError
   */
  public createOfferer({
    requestBody,
  }: {
    requestBody: CreateOffererQueryModel,
  }): CancelablePromise<PostOffererResponseModel> {
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
   * @returns GetEducationalOfferersResponseModel OK
   * @throws ApiError
   */
  public listEducationalOfferers({
    offererId,
  }: {
    offererId?: number | null,
  }): CancelablePromise<GetEducationalOfferersResponseModel> {
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
   * @returns GetOfferersNamesResponseModel OK
   * @throws ApiError
   */
  public listOfferersNames({
    validated,
    validatedForUser,
    offererId,
  }: {
    validated?: boolean | null,
    validatedForUser?: boolean | null,
    offererId?: number | null,
  }): CancelablePromise<GetOfferersNamesResponseModel> {
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
   * @returns PostOffererResponseModel Created
   * @throws ApiError
   */
  public saveNewOnboardingData({
    requestBody,
  }: {
    requestBody: SaveNewOnboardingDataQueryModel,
  }): CancelablePromise<PostOffererResponseModel> {
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
   * @returns GetOffererResponseModel OK
   * @throws ApiError
   */
  public getOfferer({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<GetOffererResponseModel> {
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
   * @returns GetOffererBankAccountsResponseModel OK
   * @throws ApiError
   */
  public getOffererBankAccountsAndAttachedVenues({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<GetOffererBankAccountsResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public linkVenueToBankAccount({
    offererId,
    bankAccountId,
    requestBody,
  }: {
    offererId: number,
    bankAccountId: number,
    requestBody: LinkVenueToBankAccountBodyModel,
  }): CancelablePromise<void> {
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
   * @returns OffererEligibilityResponseModel OK
   * @throws ApiError
   */
  public getOffererEligibility({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<OffererEligibilityResponseModel> {
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
   * @returns HeadLineOfferResponseModel OK
   * @throws ApiError
   */
  public getOffererHeadlineOffer({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<HeadLineOfferResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public inviteMember({
    offererId,
    requestBody,
  }: {
    offererId: number,
    requestBody: InviteMemberQueryModel,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public inviteMemberAgain({
    offererId,
    requestBody,
  }: {
    offererId: number,
    requestBody: InviteMemberQueryModel,
  }): CancelablePromise<void> {
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
   * @returns GetOffererMembersResponseModel OK
   * @throws ApiError
   */
  public getOffererMembers({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<GetOffererMembersResponseModel> {
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
   * @returns GetOffererAddressesResponseModel OK
   * @throws ApiError
   */
  public getOffererAddresses({
    offererId,
    withOffersOption,
  }: {
    offererId: number,
    withOffersOption?: GetOffererAddressesWithOffersOption | null,
  }): CancelablePromise<GetOffererAddressesResponseModel> {
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
   * @returns GetOffererStatsResponseModel OK
   * @throws ApiError
   */
  public getOffererStats({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<GetOffererStatsResponseModel> {
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
   * @returns GetOffererV2StatsResponseModel OK
   * @throws ApiError
   */
  public getOffererV2Stats({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<GetOffererV2StatsResponseModel> {
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
   * @returns ListOffersResponseModel OK
   * @throws ApiError
   */
  public listOffers({
    nameOrIsbn,
    offererId,
    status,
    venueId,
    categoryId,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
    collectiveOfferType,
    offererAddressId,
  }: {
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
  }): CancelablePromise<ListOffersResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * post_offer <POST>
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public postOffer({
    requestBody,
  }: {
    requestBody: PostOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public patchOffersActiveStatus({
    requestBody,
  }: {
    requestBody: PatchOfferActiveStatusBodyModel,
  }): CancelablePromise<void> {
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
   * @returns any Accepted
   * @throws ApiError
   */
  public patchAllOffersActiveStatus({
    requestBody,
  }: {
    requestBody: PatchAllOffersActiveStatusBodyModel,
  }): CancelablePromise<any> {
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
   * @returns void
   * @throws ApiError
   */
  public deleteDraftOffers({
    requestBody,
  }: {
    requestBody: DeleteOfferRequestBody,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public deleteHeadlineOffer({
    requestBody,
  }: {
    requestBody: HeadlineOfferDeleteBodyModel,
  }): CancelablePromise<void> {
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
   * @deprecated
   * [DEPRECATED] Please migrate to new (generic/standard) offer creation route
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public postDraftOffer({
    requestBody,
  }: {
    requestBody: PostDraftOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/draft',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * @deprecated
   * patch_draft_offer <PATCH>
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public patchDraftOffer({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchDraftOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public patchPublishOffer({
    requestBody,
  }: {
    requestBody: PatchOfferPublishBodyModel,
  }): CancelablePromise<GetIndividualOfferResponseModel> {
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
   * @returns CreateThumbnailResponseModel Created
   * @throws ApiError
   */
  public createThumbnail({
    formData,
  }: {
    formData: CreateThumbnailBodyModel,
  }): CancelablePromise<CreateThumbnailResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/thumbnails/',
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
   * @returns void
   * @throws ApiError
   */
  public deleteThumbnail({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<void> {
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
   * @returns HeadLineOfferResponseModel Created
   * @throws ApiError
   */
  public upsertHeadlineOffer({
    requestBody,
  }: {
    requestBody: HeadlineOfferCreationBodyModel,
  }): CancelablePromise<HeadLineOfferResponseModel> {
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
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public getOffer({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public patchOffer({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
   * @returns GetIndividualOfferWithAddressResponseModel Created
   * @throws ApiError
   */
  public postHighlightRequestOffer({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: CreateOfferHighlightRequestBodyModel,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
   * @returns OfferOpeningHoursSchema OK
   * @throws ApiError
   */
  public getOfferOpeningHours({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<OfferOpeningHoursSchema> {
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
   * @returns OfferOpeningHoursSchema OK
   * @throws ApiError
   */
  public upsertOfferOpeningHours({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: OfferOpeningHoursSchema,
  }): CancelablePromise<OfferOpeningHoursSchema> {
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
   * post_price_categories <POST>
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public postPriceCategories({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PriceCategoryBody,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * delete_price_category <DELETE>
   * @returns void
   * @throws ApiError
   */
  public deletePriceCategory({
    offerId,
    priceCategoryId,
  }: {
    offerId: number,
    priceCategoryId: number,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/offers/{offer_id}/price_categories/{price_category_id}',
      path: {
        'offer_id': offerId,
        'price_category_id': priceCategoryId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_stocks_stats <GET>
   * @returns StockStatsResponseModel OK
   * @throws ApiError
   */
  public getStocksStats({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<StockStatsResponseModel> {
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
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public getStocks({
    offerId,
    date,
    time,
    priceCategoryId,
    orderBy,
    orderByDesc = false,
    page = 1,
    stocksLimitPerPage = 20,
  }: {
    offerId: number,
    date?: string | null,
    time?: string | null,
    priceCategoryId?: number | null,
    orderBy?: StocksOrderedBy,
    orderByDesc?: boolean,
    page?: number,
    stocksLimitPerPage?: number,
  }): CancelablePromise<GetStocksResponseModel> {
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
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public upsertOfferStocks({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: ThingStocksBulkUpsertBodyModel,
  }): CancelablePromise<GetStocksResponseModel> {
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
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public deleteStocks({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: DeleteStockListBody,
  }): CancelablePromise<GetStocksResponseModel> {
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
   * @returns GetActiveEANOfferResponseModel OK
   * @throws ApiError
   */
  public getActiveVenueOfferByEan({
    venueId,
    ean,
  }: {
    venueId: number,
    ean: string,
  }): CancelablePromise<GetActiveEANOfferResponseModel> {
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
   * get_reimbursements_csv <GET>
   * @returns any OK
   * @throws ApiError
   */
  public getReimbursementsCsv({
    offererId,
    bankAccountId,
    reimbursementPeriodBeginningDate,
    reimbursementPeriodEndingDate,
  }: {
    offererId: number,
    bankAccountId?: number,
    reimbursementPeriodBeginningDate?: string,
    reimbursementPeriodEndingDate?: string,
  }): CancelablePromise<any> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * bulk_update_event_stocks <PATCH>
   * @returns GetStocksResponseModel OK
   * @throws ApiError
   */
  public bulkUpdateEventStocks({
    requestBody,
  }: {
    requestBody: EventStocksBulkUpdateBodyModel,
  }): CancelablePromise<GetStocksResponseModel> {
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
   * @returns GetStocksResponseModel Created
   * @throws ApiError
   */
  public bulkCreateEventStocks({
    requestBody,
  }: {
    requestBody: EventStocksBulkCreateBodyModel,
  }): CancelablePromise<GetStocksResponseModel> {
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
   * @returns StructureDataBodyModel OK
   * @throws ApiError
   */
  public getStructureData({
    searchInput,
  }: {
    searchInput: string,
  }): CancelablePromise<StructureDataBodyModel> {
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
   * post_check_token <POST>
   * @returns void
   * @throws ApiError
   */
  public postCheckToken({
    requestBody,
  }: {
    requestBody: CheckTokenBodyModel,
  }): CancelablePromise<void> {
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
   * @returns any OK
   * @throws ApiError
   */
  public connectAs({
    token,
  }: {
    token: string,
  }): CancelablePromise<any> {
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
   * @returns void
   * @throws ApiError
   */
  public cookiesConsent({
    requestBody,
  }: {
    requestBody: CookieConsentRequest,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public postUserEmail({
    requestBody,
  }: {
    requestBody: UserResetEmailBodyModel,
  }): CancelablePromise<void> {
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
   * @returns UserIdentityResponseModel OK
   * @throws ApiError
   */
  public patchUserIdentity({
    requestBody,
  }: {
    requestBody: UserIdentityBodyModel,
  }): CancelablePromise<UserIdentityResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public submitUserReview({
    requestBody,
  }: {
    requestBody: SubmitReviewRequestModel,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public postNewPassword({
    requestBody,
  }: {
    requestBody: NewPasswordBodyModel,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public postChangePassword({
    requestBody,
  }: {
    requestBody: ChangePasswordBodyModel,
  }): CancelablePromise<void> {
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
   * @returns UserPhoneResponseModel OK
   * @throws ApiError
   */
  public patchUserPhone({
    requestBody,
  }: {
    requestBody: UserPhoneBodyModel,
  }): CancelablePromise<UserPhoneResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public resetPassword({
    requestBody,
  }: {
    requestBody: ResetPasswordBodyModel,
  }): CancelablePromise<void> {
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
   * @returns SharedLoginUserResponseModel OK
   * @throws ApiError
   */
  public signin({
    requestBody,
  }: {
    requestBody: LoginUserBodyModel,
  }): CancelablePromise<SharedLoginUserResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public signupPro({
    requestBody,
  }: {
    requestBody: ProUserCreationBodyV2Model,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public patchValidateEmail({
    requestBody,
  }: {
    requestBody: ChangeProEmailBody,
  }): CancelablePromise<void> {
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
   * @returns void
   * @throws ApiError
   */
  public validateUser({
    token,
  }: {
    token: string,
  }): CancelablePromise<void> {
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
   * @returns HasInvoiceResponseModel OK
   * @throws ApiError
   */
  public hasInvoice({
    offererId,
  }: {
    offererId: number,
  }): CancelablePromise<HasInvoiceResponseModel> {
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
   * @returns InvoiceListV2ResponseModel OK
   * @throws ApiError
   */
  public getInvoicesV2({
    periodBeginningDate,
    periodEndingDate,
    bankAccountId,
    offererId,
  }: {
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    bankAccountId?: number | null,
    offererId?: number | null,
  }): CancelablePromise<InvoiceListV2ResponseModel> {
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
   * @returns GetIndividualOfferResponseModel Created
   * @throws ApiError
   */
  public createOffer({
    requestBody,
  }: {
    requestBody: PostOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferResponseModel> {
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
   * update_offer <PATCH>
   * @returns GetIndividualOfferWithAddressResponseModel OK
   * @throws ApiError
   */
  public updateOffer({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PatchOfferBodyModel,
  }): CancelablePromise<GetIndividualOfferWithAddressResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/v2/offers/{offer_id}',
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
   * get_reimbursements_csv_v2 <GET>
   * @returns any OK
   * @throws ApiError
   */
  public getReimbursementsCsvV2({
    invoicesReferences,
  }: {
    invoicesReferences: Array<string>,
  }): CancelablePromise<any> {
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
   * @returns GetOffersStatsResponseModel OK
   * @throws ApiError
   */
  public getOffersStatistics({
    venueId,
  }: {
    venueId: number,
  }): CancelablePromise<GetOffersStatsResponseModel> {
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
   * list_venue_providers <GET>
   * @returns ListVenueProviderResponse OK
   * @throws ApiError
   */
  public listVenueProviders({
    venueId,
  }: {
    venueId: number,
  }): CancelablePromise<ListVenueProviderResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venueProviders',
      query: {
        'venueId': venueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * create_venue_provider <POST>
   * @returns VenueProviderResponse Created
   * @throws ApiError
   */
  public createVenueProvider({
    requestBody,
  }: {
    requestBody: PostVenueProviderBody,
  }): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/venueProviders',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * update_venue_provider <PUT>
   * @returns VenueProviderResponse OK
   * @throws ApiError
   */
  public updateVenueProvider({
    requestBody,
  }: {
    requestBody: PostVenueProviderBody,
  }): CancelablePromise<VenueProviderResponse> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/venueProviders',
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
   * @returns ListProviderResponse OK
   * @throws ApiError
   */
  public getProvidersByVenue({
    venueId,
  }: {
    venueId: number,
  }): CancelablePromise<ListProviderResponse> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * delete_venue_provider <DELETE>
   * @returns void
   * @throws ApiError
   */
  public deleteVenueProvider({
    venueProviderId,
  }: {
    venueProviderId: number,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/venueProviders/{venue_provider_id}',
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
   * @deprecated
   * [deprecated] please use /lite/venues instead
   * This route loads way too much data.
   * @returns GetVenueListResponseModel OK
   * @throws ApiError
   */
  public getVenues({
    validated,
    activeOfferersOnly,
    offererId,
  }: {
    validated?: boolean | null,
    activeOfferersOnly?: boolean | null,
    offererId?: number | null,
  }): CancelablePromise<GetVenueListResponseModel> {
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
   * @returns GetVenuesOfOffererFromSiretResponseModel OK
   * @throws ApiError
   */
  public getVenuesOfOffererFromSiret({
    siret,
  }: {
    siret: string,
  }): CancelablePromise<GetVenuesOfOffererFromSiretResponseModel> {
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
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public getVenue({
    venueId,
  }: {
    venueId: number,
  }): CancelablePromise<GetVenueResponseModel> {
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
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public editVenue({
    venueId,
    requestBody,
  }: {
    venueId: number,
    requestBody: EditVenueBodyModel,
  }): CancelablePromise<GetVenueResponseModel> {
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
   * @returns void
   * @throws ApiError
   */
  public deleteVenueBanner({
    venueId,
  }: {
    venueId: number,
  }): CancelablePromise<void> {
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
   * @returns GetVenueResponseModel OK
   * @throws ApiError
   */
  public editVenueCollectiveData({
    venueId,
    requestBody,
  }: {
    venueId: number,
    requestBody: EditVenueCollectiveDataBodyModel,
  }): CancelablePromise<GetVenueResponseModel> {
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
   * link_venue_to_pricing_point <POST>
   * @returns void
   * @throws ApiError
   */
  public linkVenueToPricingPoint({
    venueId,
    requestBody,
  }: {
    venueId: number,
    requestBody: LinkVenueToPricingPointBodyModel,
  }): CancelablePromise<void> {
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
}
