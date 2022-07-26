/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdageCulturalPartnerResponseModel } from '../models/AdageCulturalPartnerResponseModel';
import type { AdageCulturalPartnersResponseModel } from '../models/AdageCulturalPartnersResponseModel';
import type { BookingExportType } from '../models/BookingExportType';
import type { BookingStatusFilter } from '../models/BookingStatusFilter';
import type { BusinessUnitEditionBodyModel } from '../models/BusinessUnitEditionBodyModel';
import type { BusinessUnitListResponseModel } from '../models/BusinessUnitListResponseModel';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { CollectiveBookingStatusFilter } from '../models/CollectiveBookingStatusFilter';
import type { CollectiveOfferFromTemplateResponseModel } from '../models/CollectiveOfferFromTemplateResponseModel';
import type { CollectiveOfferResponseIdModel } from '../models/CollectiveOfferResponseIdModel';
import type { CollectiveOfferTemplateBodyModel } from '../models/CollectiveOfferTemplateBodyModel';
import type { CollectiveOfferTemplateResponseIdModel } from '../models/CollectiveOfferTemplateResponseIdModel';
import type { CollectiveStockCreationBodyModel } from '../models/CollectiveStockCreationBodyModel';
import type { CollectiveStockEditionBodyModel } from '../models/CollectiveStockEditionBodyModel';
import type { CollectiveStockIdResponseModel } from '../models/CollectiveStockIdResponseModel';
import type { CollectiveStockResponseModel } from '../models/CollectiveStockResponseModel';
import type { CreateOffererQueryModel } from '../models/CreateOffererQueryModel';
import type { CreateThumbnailResponseModel } from '../models/CreateThumbnailResponseModel';
import type { EditVenueBodyModel } from '../models/EditVenueBodyModel';
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
import type { PatchProUserBodyModel } from '../models/PatchProUserBodyModel';
import type { PatchProUserResponseModel } from '../models/PatchProUserResponseModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';
import type { PostOfferBodyModel } from '../models/PostOfferBodyModel';
import type { PostVenueProviderBody } from '../models/PostVenueProviderBody';
import type { ReimbursementPointListResponseModel } from '../models/ReimbursementPointListResponseModel';
import type { SharedCurrentUserResponseModel } from '../models/SharedCurrentUserResponseModel';
import type { SharedLoginUserResponseModel } from '../models/SharedLoginUserResponseModel';
import type { StockIdResponseModel } from '../models/StockIdResponseModel';
import type { StockIdsResponseModel } from '../models/StockIdsResponseModel';
import type { StocksResponseModel } from '../models/StocksResponseModel';
import type { StocksUpsertBodyModel } from '../models/StocksUpsertBodyModel';
import type { UserIdentityBodyModel } from '../models/UserIdentityBodyModel';
import type { UserIdentityResponseModel } from '../models/UserIdentityResponseModel';
import type { VenueLabelListResponseModel } from '../models/VenueLabelListResponseModel';
import type { VenueProviderResponse } from '../models/VenueProviderResponse';
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
   * transform_collective_offer_template_into_collective_offer <PATCH>
   * @param offerId
   * @param requestBody
   * @returns CollectiveOfferFromTemplateResponseModel Created
   * @throws ApiError
   */
  public transformCollectiveOfferTemplateIntoCollectiveOffer(
    offerId: string,
    requestBody?: CollectiveStockCreationBodyModel,
  ): CancelablePromise<CollectiveOfferFromTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/collective/offers-template/{offer_id}/to-collective-offer',
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
   * get_collective_offers <GET>
   * @param nameOrIsbn
   * @param offererId
   * @param status
   * @param venueId
   * @param categoryId
   * @param creationMode
   * @param periodBeginningDate
   * @param periodEndingDate
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
  ): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/collective/offrs',
      query: {
        'nameOrIsbn': nameOrIsbn,
        'offererId': offererId,
        'status': status,
        'venueId': venueId,
        'categoryId': categoryId,
        'creationMode': creationMode,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
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
   * @returns InvoiceListResponseModel OK
   * @throws ApiError
   */
  public getInvoices(
    businessUnitId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
  ): CancelablePromise<InvoiceListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/finance/invoices',
      query: {
        'businessUnitId': businessUnitId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
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
   * @returns GetOfferersNamesResponseModel OK
   * @throws ApiError
   */
  public listOfferersNames(
    validated?: boolean | null,
    validatedForUser?: boolean | null,
  ): CancelablePromise<GetOfferersNamesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/offerers/names',
      query: {
        'validated': validated,
        'validated_for_user': validatedForUser,
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
   * patch_profile <PATCH>
   * @param requestBody
   * @returns PatchProUserResponseModel OK
   * @throws ApiError
   */
  public patchProfile(
    requestBody?: PatchProUserBodyModel,
  ): CancelablePromise<PatchProUserResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/users/current',
      body: requestBody,
      mediaType: 'application/json',
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
    offererId?: number | null,
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
