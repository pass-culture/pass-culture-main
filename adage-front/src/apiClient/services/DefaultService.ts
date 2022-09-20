/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthenticatedResponse } from '../models/AuthenticatedResponse';
import type { BookCollectiveOfferRequest } from '../models/BookCollectiveOfferRequest';
import type { BookCollectiveOfferResponse } from '../models/BookCollectiveOfferResponse';
import type { CatalogViewBody } from '../models/CatalogViewBody';
import type { CategoriesResponseModel } from '../models/CategoriesResponseModel';
import type { CollectiveOfferResponseModel } from '../models/CollectiveOfferResponseModel';
import type { CollectiveOfferTemplateResponseModel } from '../models/CollectiveOfferTemplateResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { OfferIdBody } from '../models/OfferIdBody';
import type { SearchBody } from '../models/SearchBody';
import type { StockIdBody } from '../models/StockIdBody';
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
   * get_venue_by_siret <GET>
   * @param siret
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueBySiret(
    siret: string,
  ): CancelablePromise<VenueResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/venues/siret/{siret}',
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
   * get_venue_by_id <GET>
   * @param venueId
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueById(
    venueId: number,
  ): CancelablePromise<VenueResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/venues/{venue_id}',
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
