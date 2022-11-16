/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdageCulturalPartnerResponseModel } from '../models/AdageCulturalPartnerResponseModel';
import type { AdageCulturalPartnersResponseModel } from '../models/AdageCulturalPartnersResponseModel';
import type { AttachImageResponseModel } from '../models/AttachImageResponseModel';
import type { BookingExportType } from '../models/BookingExportType';
import type { BookingStatusFilter } from '../models/BookingStatusFilter';
import type { BusinessUnitEditionBodyModel } from '../models/BusinessUnitEditionBodyModel';
import type { BusinessUnitListResponseModel } from '../models/BusinessUnitListResponseModel';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { ChangePasswordBodyModel } from '../models/ChangePasswordBodyModel';
import type { ChangeProEmailBody } from '../models/ChangeProEmailBody';
import type { CollectiveBookingByIdResponseModel } from '../models/CollectiveBookingByIdResponseModel';
import type { CollectiveBookingStatusFilter } from '../models/CollectiveBookingStatusFilter';
import type { CollectiveOfferResponseIdModel } from '../models/CollectiveOfferResponseIdModel';
import type { CollectiveOfferTemplateBodyModel } from '../models/CollectiveOfferTemplateBodyModel';
import type { CollectiveOfferTemplateResponseIdModel } from '../models/CollectiveOfferTemplateResponseIdModel';
import type { CollectiveOfferType } from '../models/CollectiveOfferType';
import type { CollectiveStockCreationBodyModel } from '../models/CollectiveStockCreationBodyModel';
import type { CollectiveStockEditionBodyModel } from '../models/CollectiveStockEditionBodyModel';
import type { CollectiveStockIdResponseModel } from '../models/CollectiveStockIdResponseModel';
import type { CollectiveStockResponseModel } from '../models/CollectiveStockResponseModel';
import type { CreateOffererQueryModel } from '../models/CreateOffererQueryModel';
import type { CreateThumbnailResponseModel } from '../models/CreateThumbnailResponseModel';
import type { DeleteOfferRequestBody } from '../models/DeleteOfferRequestBody';
import type { EditVenueBodyModel } from '../models/EditVenueBodyModel';
import type { EditVenueCollectiveDataBodyModel } from '../models/EditVenueCollectiveDataBodyModel';
import type { EducationalDomainsResponseModel } from '../models/EducationalDomainsResponseModel';
import type { EducationalInstitutionsResponseModel } from '../models/EducationalInstitutionsResponseModel';
import type { GenerateOffererApiKeyResponse } from '../models/GenerateOffererApiKeyResponse';
import type { GetCollectiveOfferResponseModel } from '../models/GetCollectiveOfferResponseModel';
import type { GetCollectiveOfferTemplateResponseModel } from '../models/GetCollectiveOfferTemplateResponseModel';
import type { GetCollectiveVenueResponseModel } from '../models/GetCollectiveVenueResponseModel';
import type { GetEducationalOfferersResponseModel } from '../models/GetEducationalOfferersResponseModel';
import type { GetIndividualOfferResponseModel } from '../models/GetIndividualOfferResponseModel';
import type { GetOffererResponseModel } from '../models/GetOffererResponseModel';
import type { GetOfferersListResponseModel } from '../models/GetOfferersListResponseModel';
import type { GetOfferersNamesResponseModel } from '../models/GetOfferersNamesResponseModel';
import type { GetVenueListResponseModel } from '../models/GetVenueListResponseModel';
import type { GetVenueResponseModel } from '../models/GetVenueResponseModel';
import type { InvoiceListResponseModel } from '../models/InvoiceListResponseModel';
import type { LinkVenueToPricingPointBodyModel } from '../models/LinkVenueToPricingPointBodyModel';
import type { ListBookingsResponseModel } from '../models/ListBookingsResponseModel';
import type { ListCollectiveBookingsResponseModel } from '../models/ListCollectiveBookingsResponseModel';
import type { ListCollectiveOffersResponseModel } from '../models/ListCollectiveOffersResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { ListOffersResponseModel } from '../models/ListOffersResponseModel';
import type { ListVenueProviderResponse } from '../models/ListVenueProviderResponse';
import type { LoginUserBodyModel } from '../models/LoginUserBodyModel';
import type { NewPasswordBodyModel } from '../models/NewPasswordBodyModel';
import type { OffererStatsResponseModel } from '../models/OffererStatsResponseModel';
import type { OfferResponseIdModel } from '../models/OfferResponseIdModel';
import type { OfferType } from '../models/OfferType';
import type { PatchAllCollectiveOffersActiveStatusBodyModel } from '../models/PatchAllCollectiveOffersActiveStatusBodyModel';
import type { PatchAllOffersActiveStatusBodyModel } from '../models/PatchAllOffersActiveStatusBodyModel';
import type { PatchCollectiveOfferActiveStatusBodyModel } from '../models/PatchCollectiveOfferActiveStatusBodyModel';
import type { PatchCollectiveOfferBodyModel } from '../models/PatchCollectiveOfferBodyModel';
import type { PatchCollectiveOfferEducationalInstitution } from '../models/PatchCollectiveOfferEducationalInstitution';
import type { PatchCollectiveOfferTemplateBodyModel } from '../models/PatchCollectiveOfferTemplateBodyModel';
import type { PatchOfferActiveStatusBodyModel } from '../models/PatchOfferActiveStatusBodyModel';
import type { PatchOfferBodyModel } from '../models/PatchOfferBodyModel';
import type { PatchOfferPublishBodyModel } from '../models/PatchOfferPublishBodyModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';
import type { PostCollectiveOfferTemplateBodyModel } from '../models/PostCollectiveOfferTemplateBodyModel';
import type { PostOfferBodyModel } from '../models/PostOfferBodyModel';
import type { PostVenueBodyModel } from '../models/PostVenueBodyModel';
import type { PostVenueProviderBody } from '../models/PostVenueProviderBody';
import type { ProUserCreationBodyModel } from '../models/ProUserCreationBodyModel';
import type { ReimbursementPointListResponseModel } from '../models/ReimbursementPointListResponseModel';
import type { ResetPasswordBodyModel } from '../models/ResetPasswordBodyModel';
import type { SharedCurrentUserResponseModel } from '../models/SharedCurrentUserResponseModel';
import type { SharedLoginUserResponseModel } from '../models/SharedLoginUserResponseModel';
import type { SirenInfo } from '../models/SirenInfo';
import type { SiretInfo } from '../models/SiretInfo';
import type { StockIdResponseModel } from '../models/StockIdResponseModel';
import type { StockIdsResponseModel } from '../models/StockIdsResponseModel';
import type { StocksResponseModel } from '../models/StocksResponseModel';
import type { StocksUpsertBodyModel } from '../models/StocksUpsertBodyModel';
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
   * get_bookings_pro <GET>
   * @param page
   * @param venueId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @param offerType
   * @param exportType
   * @param extra
   * @returns ListBookingsResponseModel OK
   * @throws ApiError
   */
  public getBookingsPro(
    page: number = 1,
    venueId?: number | null,
    eventDate?: string | null,
    bookingStatusFilter?: BookingStatusFilter | null,
    bookingPeriodBeginningDate?: string | null,
    bookingPeriodEndingDate?: string | null,
    offerType?: OfferType | null,
    exportType?: BookingExportType | null,
    extra: string = 'forbid',
  ): CancelablePromise<ListBookingsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/bookings/pro',
      query: {
        'page': page,
        'venueId': venueId,
        'eventDate': eventDate,
        'bookingStatusFilter': bookingStatusFilter,
        'bookingPeriodBeginningDate': bookingPeriodBeginningDate,
        'bookingPeriodEndingDate': bookingPeriodEndingDate,
        'offerType': offerType,
        'exportType': exportType,
        'extra': extra,
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
   * get_collective_bookings_pro <GET>
   * @param page
   * @param venueId
   * @param eventDate
   * @param bookingStatusFilter
   * @param bookingPeriodBeginningDate
   * @param bookingPeriodEndingDate
   * @param extra
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
    extra: string = 'forbid',
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
        'extra': extra,
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
    bookingId: string,
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
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffers(
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: string | null,
    venueId?: number | null,
    categoryId?: string | null,
    creationMode?: string | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    collectiveOfferType?: CollectiveOfferType | null,
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
   * get_collective_offer_template <GET>
   * @param offerId
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplate(
    offerId: string,
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
    offerId: string,
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
    offerId: string,
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
   * attach_offer_template_image <PATCH>
   * @param offerId
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferTemplateImage(
    offerId: string,
  ): CancelablePromise<AttachImageResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
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
   * patch_collective_offer_template_publication <PATCH>
   * @param offerId
   * @returns GetCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferTemplatePublication(
    offerId: string,
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
   * get_collective_offer <GET>
   * @param offerId
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffer(
    offerId: string,
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
    offerId: string,
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
    offerId: string,
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
   * patch_collective_offers_educational_institution <PATCH>
   * @param offerId
   * @param requestBody
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOffersEducationalInstitution(
    offerId: string,
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
   * attach_offer_image <PATCH>
   * @param offerId
   * @returns AttachImageResponseModel OK
   * @throws ApiError
   */
  public attachOfferImage(
    offerId: string,
  ): CancelablePromise<AttachImageResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
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
   * patch_collective_offer_publication <PATCH>
   * @param offerId
   * @returns GetCollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public patchCollectiveOfferPublication(
    offerId: string,
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
   * get_collective_stock <GET>
   * @param offerId
   * @returns CollectiveStockResponseModel OK
   * @throws ApiError
   */
  public getCollectiveStock(
    offerId: string,
  ): CancelablePromise<CollectiveStockResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offers/{offer_id}/stock',
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
   * create_collective_stock <POST>
   * @param requestBody
   * @returns CollectiveStockIdResponseModel Created
   * @throws ApiError
   */
  public createCollectiveStock(
    requestBody?: CollectiveStockCreationBodyModel,
  ): CancelablePromise<CollectiveStockIdResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/collective/stocks',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
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
    collectiveStockId: string,
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
   * get_educational_partner <GET>
   * @param siret
   * @returns AdageCulturalPartnerResponseModel OK
   * @throws ApiError
   */
  public getEducationalPartner(
    siret: string,
  ): CancelablePromise<AdageCulturalPartnerResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/cultural-partner/{siret}',
      path: {
        'siret': siret,
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
   * get_business_units <GET>
   * @param offererId
   * @returns BusinessUnitListResponseModel OK
   * @throws ApiError
   */
  public getBusinessUnits(
    offererId?: number | null,
  ): CancelablePromise<BusinessUnitListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/business-units',
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
   * edit_business_unit <PATCH>
   * @param businessUnitId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public editBusinessUnit(
    businessUnitId: number,
    requestBody?: BusinessUnitEditionBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/finance/business-units/{business_unit_id}',
      path: {
        'business_unit_id': businessUnitId,
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
   * get_invoices <GET>
   * @param businessUnitId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @param reimbursementPointId
   * @returns InvoiceListResponseModel OK
   * @throws ApiError
   */
  public getInvoices(
    businessUnitId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    reimbursementPointId?: number | null,
  ): CancelablePromise<InvoiceListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/invoices',
      query: {
        'businessUnitId': businessUnitId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
        'reimbursementPointId': reimbursementPointId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_reimbursement_points <GET>
   * @param offererId
   * @returns ReimbursementPointListResponseModel OK
   * @throws ApiError
   */
  public getReimbursementPoints(
    offererId?: number | null,
  ): CancelablePromise<ReimbursementPointListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/reimbursement-points',
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
   * get_offerers <GET>
   * @param keywords
   * @param page
   * @param paginate
   * @returns GetOfferersListResponseModel OK
   * @throws ApiError
   */
  public getOfferers(
    keywords?: string | null,
    page: number | null = 1,
    paginate: number | null = 10,
  ): CancelablePromise<GetOfferersListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers',
      query: {
        'keywords': keywords,
        'page': page,
        'paginate': paginate,
      },
      errors: {
        400: `Bad Request`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * create_offerer <POST>
   * @param requestBody
   * @returns GetOffererResponseModel Created
   * @throws ApiError
   */
  public createOfferer(
    requestBody?: CreateOffererQueryModel,
  ): CancelablePromise<GetOffererResponseModel> {
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
    offererId?: string | null,
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
    offererId?: string | null,
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
   * can_offerer_create_educational_offer <GET>
   * @param humanizedOffererId
   * @returns void
   * @throws ApiError
   */
  public canOffererCreateEducationalOffer(
    humanizedOffererId: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{humanized_offerer_id}/eac-eligibility',
      path: {
        'humanized_offerer_id': humanizedOffererId,
      },
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
    offererId: string,
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
   * generate_api_key_route <POST>
   * @param offererId
   * @returns GenerateOffererApiKeyResponse OK
   * @throws ApiError
   */
  public generateApiKeyRoute(
    offererId: string,
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
   * get_offerer_stats_dashboard_url <GET>
   * @param offererId
   * @returns OffererStatsResponseModel OK
   * @throws ApiError
   */
  public getOffererStatsDashboardUrl(
    offererId: string,
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
   * get_available_reimbursement_points <GET>
   * @param offererId
   * @returns ReimbursementPointListResponseModel OK
   * @throws ApiError
   */
  public getAvailableReimbursementPoints(
    offererId: number,
  ): CancelablePromise<ReimbursementPointListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/{offerer_id}/reimbursement-points',
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
   * @returns ListOffersResponseModel OK
   * @throws ApiError
   */
  public listOffers(
    nameOrIsbn?: string | null,
    offererId?: number | null,
    status?: string | null,
    venueId?: number | null,
    categoryId?: string | null,
    creationMode?: string | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
    collectiveOfferType?: CollectiveOfferType | null,
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
   * @returns OfferResponseIdModel Created
   * @throws ApiError
   */
  public postOffer(
    requestBody?: PostOfferBodyModel,
  ): CancelablePromise<OfferResponseIdModel> {
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
   * patch_publish_offer <PATCH>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public patchPublishOffer(
    requestBody?: PatchOfferPublishBodyModel,
  ): CancelablePromise<void> {
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
   * create_thumbnail <POST>
   * @returns CreateThumbnailResponseModel Created
   * @throws ApiError
   */
  public createThumbnail(): CancelablePromise<CreateThumbnailResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/offers/thumbnails/',
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
    offerId: string,
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
   * @returns GetIndividualOfferResponseModel OK
   * @throws ApiError
   */
  public getOffer(
    offerId: string,
  ): CancelablePromise<GetIndividualOfferResponseModel> {
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
   * @returns OfferResponseIdModel OK
   * @throws ApiError
   */
  public patchOffer(
    offerId: string,
    requestBody?: PatchOfferBodyModel,
  ): CancelablePromise<OfferResponseIdModel> {
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
   * get_stocks <GET>
   * @param offerId
   * @returns StocksResponseModel OK
   * @throws ApiError
   */
  public getStocks(
    offerId: string,
  ): CancelablePromise<StocksResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offers/{offer_id}/stocks',
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
   * get_reimbursements_csv <GET>
   * @param venueId
   * @param reimbursementPeriodBeginningDate
   * @param reimbursementPeriodEndingDate
   * @returns any OK
   * @throws ApiError
   */
  public getReimbursementsCsv(
    venueId?: string,
    reimbursementPeriodBeginningDate?: string,
    reimbursementPeriodEndingDate?: string,
  ): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/reimbursements/csv',
      query: {
        'venueId': venueId,
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
   * @returns StockIdsResponseModel Created
   * @throws ApiError
   */
  public upsertStocks(
    requestBody?: StocksUpsertBodyModel,
  ): CancelablePromise<StockIdsResponseModel> {
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
    stockId: string,
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
   * signup_pro <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public signupPro(
    requestBody?: ProUserCreationBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/users/signup/pro',
      body: requestBody,
      mediaType: 'application/json',
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
   * delete_venue_provider <DELETE>
   * @param venueProviderId
   * @returns void
   * @throws ApiError
   */
  public deleteVenueProvider(
    venueProviderId: string,
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
   * @param validatedForUser
   * @param validated
   * @param activeOfferersOnly
   * @param offererId
   * @returns GetVenueListResponseModel OK
   * @throws ApiError
   */
  public getVenues(
    validatedForUser?: boolean | null,
    validated?: boolean | null,
    activeOfferersOnly?: boolean | null,
    offererId?: string | null,
  ): CancelablePromise<GetVenueListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues',
      query: {
        'validatedForUser': validatedForUser,
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
   * get_venue_stats_dashboard_url <GET>
   * @param humanizedVenueId
   * @returns OffererStatsResponseModel OK
   * @throws ApiError
   */
  public getVenueStatsDashboardUrl(
    humanizedVenueId: string,
  ): CancelablePromise<OffererStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{humanized_venue_id}/dashboard',
      path: {
        'humanized_venue_id': humanizedVenueId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_venue_stats <GET>
   * @param humanizedVenueId
   * @returns VenueStatsResponseModel OK
   * @throws ApiError
   */
  public getVenueStats(
    humanizedVenueId: string,
  ): CancelablePromise<VenueStatsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{humanized_venue_id}/stats',
      path: {
        'humanized_venue_id': humanizedVenueId,
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
    venueId: string,
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
    venueId: string,
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
    venueId: string,
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
   * get_venue_collective_data <GET>
   * @param venueId
   * @returns GetCollectiveVenueResponseModel OK
   * @throws ApiError
   */
  public getVenueCollectiveData(
    venueId: string,
  ): CancelablePromise<GetCollectiveVenueResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/venues/{venue_id}/collective-data',
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
    venueId: string,
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
   * link_venue_to_pricing_point <POST>
   * @param venueId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public linkVenueToPricingPoint(
    venueId: string,
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

}
