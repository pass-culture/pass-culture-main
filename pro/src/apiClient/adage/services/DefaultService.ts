/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AcademiesResponseModel } from '../models/AcademiesResponseModel';
import type { AdageBaseModel } from '../models/AdageBaseModel';
import type { AdageHeaderLogBody } from '../models/AdageHeaderLogBody';
import type { AuthenticatedResponse } from '../models/AuthenticatedResponse';
import type { BookCollectiveOfferRequest } from '../models/BookCollectiveOfferRequest';
import type { BookCollectiveOfferResponse } from '../models/BookCollectiveOfferResponse';
import type { CatalogViewBody } from '../models/CatalogViewBody';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { CollectiveOfferResponseModel } from '../models/CollectiveOfferResponseModel';
import type { CollectiveOfferTemplateResponseModel } from '../models/CollectiveOfferTemplateResponseModel';
import type { CollectiveRequestBody } from '../models/CollectiveRequestBody';
import type { CollectiveRequestResponseModel } from '../models/CollectiveRequestResponseModel';
import type { EducationalInstitutionWithBudgetResponseModel } from '../models/EducationalInstitutionWithBudgetResponseModel';
import type { FavoritesResponseModel } from '../models/FavoritesResponseModel';
import type { ListCollectiveOffersResponseModel } from '../models/ListCollectiveOffersResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { OfferFavoriteBody } from '../models/OfferFavoriteBody';
import type { OfferIdBody } from '../models/OfferIdBody';
import type { PostCollectiveRequestBodyModel } from '../models/PostCollectiveRequestBodyModel';
import type { RedactorPreferences } from '../models/RedactorPreferences';
import type { SearchBody } from '../models/SearchBody';
import type { StockIdBody } from '../models/StockIdBody';
import type { TrackingAutocompleteSuggestionBody } from '../models/TrackingAutocompleteSuggestionBody';
import type { TrackingFilterBody } from '../models/TrackingFilterBody';
import type { VenueResponse } from '../models/VenueResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

  /**
   * authenticate <GET>
   * @returns AuthenticatedResponse OK
   * @throws ApiError
   */
  public authenticate(): CancelablePromise<AuthenticatedResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/authenticate',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_academies <GET>
   * @returns AcademiesResponseModel OK
   * @throws ApiError
   */
  public getAcademies(): CancelablePromise<AcademiesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/academies',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_educational_eligible_offers_by_uai <GET>
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getEducationalEligibleOffersByUai(): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/all-offers',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * book_collective_offer <POST>
   * @param requestBody
   * @returns BookCollectiveOfferResponse OK
   * @throws ApiError
   */
  public bookCollectiveOffer(
    requestBody?: BookCollectiveOfferRequest,
  ): CancelablePromise<BookCollectiveOfferResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/bookings',
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
   * get_collective_favorites <GET>
   * @returns FavoritesResponseModel OK
   * @throws ApiError
   */
  public getCollectiveFavorites(): CancelablePromise<FavoritesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/favorites',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_educational_institution_with_budget <GET>
   * @returns EducationalInstitutionWithBudgetResponseModel OK
   * @throws ApiError
   */
  public getEducationalInstitutionWithBudget(): CancelablePromise<EducationalInstitutionWithBudgetResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/institution',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * delete_favorite_for_collective_offer <DELETE>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public deleteFavoriteForCollectiveOffer(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/adage-iframe/collective/offer/{offer_id}/favorites',
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
   * get_collective_offer_template <GET>
   * @param offerId
   * @returns CollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplate(
    offerId: number,
  ): CancelablePromise<CollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers-template/{offer_id}',
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
   * create_collective_request <POST>
   * @param offerId
   * @param requestBody
   * @returns CollectiveRequestResponseModel OK
   * @throws ApiError
   */
  public createCollectiveRequest(
    offerId: number,
    requestBody?: PostCollectiveRequestBodyModel,
  ): CancelablePromise<CollectiveRequestResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/offers-template/{offer_id}/request',
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
   * get_collective_offer <GET>
   * @param offerId
   * @returns CollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffer(
    offerId: number,
  ): CancelablePromise<CollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers/{offer_id}',
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
   * post_collective_offer_favorites <POST>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public postCollectiveOfferFavorites(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/offers/{offer_id}/favorites',
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
   * delete_favorite_for_collective_offer_template <DELETE>
   * @param offerTemplateId
   * @returns void
   * @throws ApiError
   */
  public deleteFavoriteForCollectiveOfferTemplate(
    offerTemplateId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/adage-iframe/collective/template/{offer_template_id}/favorites',
      path: {
        'offer_template_id': offerTemplateId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * post_collective_template_favorites <POST>
   * @param offerId
   * @returns void
   * @throws ApiError
   */
  public postCollectiveTemplateFavorites(
    offerId: number,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/templates/{offer_id}/favorites',
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
   * list_features <GET>
   * @returns ListFeatureResponseModel OK
   * @throws ApiError
   */
  public listFeatures(): CancelablePromise<ListFeatureResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/features',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * log_booking_modal_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logBookingModalButtonClick(
    requestBody?: StockIdBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/booking-modal-button',
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
   * log_catalog_view <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logCatalogView(
    requestBody?: CatalogViewBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/catalog-view',
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
   * log_contact_modal_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logContactModalButtonClick(
    requestBody?: OfferIdBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/contact-modal-button',
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
   * log_fav_offer_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logFavOfferButtonClick(
    requestBody?: OfferFavoriteBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/fav-offer/',
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
   * log_header_link_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logHeaderLinkClick(
    requestBody?: AdageHeaderLogBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/header-link-click/',
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
   * log_offer_details_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logOfferDetailsButtonClick(
    requestBody?: StockIdBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/offer-detail',
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
   * log_offer_template_details_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logOfferTemplateDetailsButtonClick(
    requestBody?: OfferIdBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/offer-template-detail',
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
   * log_request_form_popin_dismiss <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logRequestFormPopinDismiss(
    requestBody?: CollectiveRequestBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/request-popin-dismiss',
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
   * log_open_satisfaction_survey <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logOpenSatisfactionSurvey(
    requestBody?: AdageBaseModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/sat-survey',
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
   * log_search_button_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logSearchButtonClick(
    requestBody?: SearchBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/search-button',
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
   * log_tracking_autocomplete_suggestion_click <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logTrackingAutocompleteSuggestionClick(
    requestBody?: TrackingAutocompleteSuggestionBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-autocompletion',
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
   * log_tracking_filter <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logTrackingFilter(
    requestBody?: TrackingFilterBody,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-filter',
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
   * log_tracking_map <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public logTrackingMap(
    requestBody?: AdageBaseModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-map',
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
   * get_educational_offers_categories <GET>
   * @returns CategoriesResponseModel OK
   * @throws ApiError
   */
  public getEducationalOffersCategories(): CancelablePromise<CategoriesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/offers/categories',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * save_redactor_preferences <POST>
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public saveRedactorPreferences(
    requestBody?: RedactorPreferences,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/redactor/preferences',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_venue_by_siret <GET>
   * @param siret
   * @param getRelative
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueBySiret(
    siret: string,
    getRelative: boolean = false,
  ): CancelablePromise<VenueResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/venues/siret/{siret}',
      path: {
        'siret': siret,
      },
      query: {
        'getRelative': getRelative,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * get_venue_by_id <GET>
   * @param venueId
   * @param getRelative
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueById(
    venueId: number,
    getRelative: boolean = false,
  ): CancelablePromise<VenueResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/venues/{venue_id}',
      path: {
        'venue_id': venueId,
      },
      query: {
        'getRelative': getRelative,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

}
