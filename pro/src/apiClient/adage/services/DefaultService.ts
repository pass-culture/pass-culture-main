/* generated using openapi-typescript-codegen -- do not edit */
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
import type { CollectiveOfferResponseModel } from '../models/CollectiveOfferResponseModel';
import type { CollectiveOfferTemplateResponseModel } from '../models/CollectiveOfferTemplateResponseModel';
import type { CollectiveRequestBody } from '../models/CollectiveRequestBody';
import type { CollectiveRequestResponseModel } from '../models/CollectiveRequestResponseModel';
import type { ConsultOfferBody } from '../models/ConsultOfferBody';
import type { EducationalInstitutionWithBudgetResponseModel } from '../models/EducationalInstitutionWithBudgetResponseModel';
import type { FavoritesResponseModel } from '../models/FavoritesResponseModel';
import type { HighlightBannerBody } from '../models/HighlightBannerBody';
import type { ListCollectiveOffersResponseModel } from '../models/ListCollectiveOffersResponseModel';
import type { ListCollectiveOfferTemplateResponseModel } from '../models/ListCollectiveOfferTemplateResponseModel';
import type { ListFeatureResponseModel } from '../models/ListFeatureResponseModel';
import type { LocalOfferersPlaylist } from '../models/LocalOfferersPlaylist';
import type { OfferBody } from '../models/OfferBody';
import type { OfferFavoriteBody } from '../models/OfferFavoriteBody';
import type { OfferIdBody } from '../models/OfferIdBody';
import type { OfferListSwitch } from '../models/OfferListSwitch';
import type { PlaylistBody } from '../models/PlaylistBody';
import type { PostCollectiveRequestBodyModel } from '../models/PostCollectiveRequestBodyModel';
import type { RedactorPreferences } from '../models/RedactorPreferences';
import type { SearchBody } from '../models/SearchBody';
import type { StockIdBody } from '../models/StockIdBody';
import type { TrackingAutocompleteSuggestionBody } from '../models/TrackingAutocompleteSuggestionBody';
import type { TrackingCTAShareBody } from '../models/TrackingCTAShareBody';
import type { TrackingFilterBody } from '../models/TrackingFilterBody';
import type { TrackingShowMoreBody } from '../models/TrackingShowMoreBody';
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * book_collective_offer <POST>
   * @returns BookCollectiveOfferResponse OK
   * @throws ApiError
   */
  public bookCollectiveOffer({
    requestBody,
  }: {
    requestBody: BookCollectiveOfferRequest,
  }): CancelablePromise<BookCollectiveOfferResponse> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/bookings',
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
        422: `Unprocessable Content`,
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offer_templates <GET>
   * @returns ListCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplates({
    ids,
  }: {
    ids: Array<number>,
  }): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers-template/',
      query: {
        'ids': ids,
      },
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offer_template <GET>
   * @returns CollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOfferTemplate({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<CollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers-template/{offer_id}',
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
   * create_collective_request <POST>
   * @returns CollectiveRequestResponseModel OK
   * @throws ApiError
   */
  public createCollectiveRequest({
    offerId,
    requestBody,
  }: {
    offerId: number,
    requestBody: PostCollectiveRequestBodyModel,
  }): CancelablePromise<CollectiveRequestResponseModel> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offers_for_my_institution <GET>
   * @returns ListCollectiveOffersResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffersForMyInstitution(): CancelablePromise<ListCollectiveOffersResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers/my_institution',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_collective_offer <GET>
   * @returns CollectiveOfferResponseModel OK
   * @throws ApiError
   */
  public getCollectiveOffer({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<CollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/collective/offers/{offer_id}',
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
   * delete_favorite_for_collective_offer_template <DELETE>
   * @returns void
   * @throws ApiError
   */
  public deleteFavoriteForCollectiveOfferTemplate({
    offerTemplateId,
  }: {
    offerTemplateId: number,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/adage-iframe/collective/template/{offer_template_id}/favorites',
      path: {
        'offer_template_id': offerTemplateId,
      },
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * post_collective_template_favorites <POST>
   * @returns void
   * @throws ApiError
   */
  public postCollectiveTemplateFavorites({
    offerId,
  }: {
    offerId: number,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/collective/templates/{offer_id}/favorites',
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * log_booking_modal_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logBookingModalButtonClick({
    requestBody,
  }: {
    requestBody: StockIdBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/booking-modal-button',
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
   * log_catalog_view <POST>
   * @returns void
   * @throws ApiError
   */
  public logCatalogView({
    requestBody,
  }: {
    requestBody: CatalogViewBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/catalog-view',
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
   * log_consult_offer <POST>
   * @returns void
   * @throws ApiError
   */
  public logConsultOffer({
    requestBody,
  }: {
    requestBody: ConsultOfferBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/consult-offer',
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
   * log_consult_playlist_element <POST>
   * @returns void
   * @throws ApiError
   */
  public logConsultPlaylistElement({
    requestBody,
  }: {
    requestBody: PlaylistBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/consult-playlist-element',
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
   * log_contact_modal_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logContactModalButtonClick({
    requestBody,
  }: {
    requestBody: OfferBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/contact-modal-button',
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
   * log_contact_url_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logContactUrlClick({
    requestBody,
  }: {
    requestBody: OfferIdBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/contact-url-click',
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
   * log_fav_offer_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logFavOfferButtonClick({
    requestBody,
  }: {
    requestBody: OfferFavoriteBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/fav-offer/',
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
   * log_has_seen_whole_playlist <POST>
   * @returns void
   * @throws ApiError
   */
  public logHasSeenWholePlaylist({
    requestBody,
  }: {
    requestBody: PlaylistBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/has-seen-whole-playlist/',
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
   * log_header_link_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logHeaderLinkClick({
    requestBody,
  }: {
    requestBody: AdageHeaderLogBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/header-link-click/',
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
   * log_open_highlight_banner <POST>
   * @returns void
   * @throws ApiError
   */
  public logOpenHighlightBanner({
    requestBody,
  }: {
    requestBody: HighlightBannerBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/highlight-banner',
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
   * log_offer_details_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logOfferDetailsButtonClick({
    requestBody,
  }: {
    requestBody: StockIdBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/offer-detail',
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
   * log_offer_list_view_switch <POST>
   * @returns void
   * @throws ApiError
   */
  public logOfferListViewSwitch({
    requestBody,
  }: {
    requestBody: OfferListSwitch,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/offer-list-view-switch',
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
   * log_offer_template_details_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logOfferTemplateDetailsButtonClick({
    requestBody,
  }: {
    requestBody: OfferIdBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/offer-template-detail',
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
   * log_has_seen_all_playlist <POST>
   * @returns void
   * @throws ApiError
   */
  public logHasSeenAllPlaylist({
    requestBody,
  }: {
    requestBody: AdageBaseModel,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/playlist',
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
   * log_request_form_popin_dismiss <POST>
   * @returns void
   * @throws ApiError
   */
  public logRequestFormPopinDismiss({
    requestBody,
  }: {
    requestBody: CollectiveRequestBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/request-popin-dismiss',
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
   * log_open_satisfaction_survey <POST>
   * @returns void
   * @throws ApiError
   */
  public logOpenSatisfactionSurvey({
    requestBody,
  }: {
    requestBody: AdageBaseModel,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/sat-survey',
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
   * log_search_button_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logSearchButtonClick({
    requestBody,
  }: {
    requestBody: SearchBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/search-button',
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
   * log_search_show_more <POST>
   * @returns void
   * @throws ApiError
   */
  public logSearchShowMore({
    requestBody,
  }: {
    requestBody: TrackingShowMoreBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/search-show-more',
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
   * log_tracking_autocomplete_suggestion_click <POST>
   * @returns void
   * @throws ApiError
   */
  public logTrackingAutocompleteSuggestionClick({
    requestBody,
  }: {
    requestBody: TrackingAutocompleteSuggestionBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-autocompletion',
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
   * log_tracking_cta_share <POST>
   * @returns void
   * @throws ApiError
   */
  public logTrackingCtaShare({
    requestBody,
  }: {
    requestBody: TrackingCTAShareBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-cta-share',
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
   * log_tracking_filter <POST>
   * @returns void
   * @throws ApiError
   */
  public logTrackingFilter({
    requestBody,
  }: {
    requestBody: TrackingFilterBody,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-filter',
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
   * log_tracking_map <POST>
   * @returns void
   * @throws ApiError
   */
  public logTrackingMap({
    requestBody,
  }: {
    requestBody: AdageBaseModel,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/logs/tracking-map',
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
   * get_classroom_playlist <GET>
   * @returns ListCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public getClassroomPlaylist(): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/playlists/classroom',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_local_offerers_playlist <GET>
   * @returns LocalOfferersPlaylist OK
   * @throws ApiError
   */
  public getLocalOfferersPlaylist(): CancelablePromise<LocalOfferersPlaylist> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/playlists/local-offerers',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_new_offerers_playlist <GET>
   * @returns LocalOfferersPlaylist OK
   * @throws ApiError
   */
  public getNewOfferersPlaylist(): CancelablePromise<LocalOfferersPlaylist> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/playlists/new_offerers',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * new_template_offers_playlist <GET>
   * @returns ListCollectiveOfferTemplateResponseModel OK
   * @throws ApiError
   */
  public newTemplateOffersPlaylist(): CancelablePromise<ListCollectiveOfferTemplateResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/playlists/new_template_offers',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * save_redactor_preferences <POST>
   * @returns void
   * @throws ApiError
   */
  public saveRedactorPreferences({
    requestBody,
  }: {
    requestBody: RedactorPreferences,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/adage-iframe/redactor/preferences',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        403: `Forbidden`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * create_adage_jwt_fake_token <GET>
   * @returns any OK
   * @throws ApiError
   */
  public createAdageJwtFakeToken(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/adage-iframe/testing/token',
      errors: {
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_venue_by_siret <GET>
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueBySiret({
    siret,
    getRelative = false,
  }: {
    siret: string,
    getRelative?: boolean,
  }): CancelablePromise<VenueResponse> {
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
        422: `Unprocessable Content`,
      },
    });
  }
  /**
   * get_venue_by_id <GET>
   * @returns VenueResponse OK
   * @throws ApiError
   */
  public getVenueById({
    venueId,
    getRelative = false,
  }: {
    venueId: number,
    getRelative?: boolean,
  }): CancelablePromise<VenueResponse> {
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
        422: `Unprocessable Content`,
      },
    });
  }
}
