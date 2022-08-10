/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOffersListCategoriesResponseModel } from '../models/CollectiveOffersListCategoriesResponseModel';
import type { CollectiveOffersListDomainsResponseModel } from '../models/CollectiveOffersListDomainsResponseModel';
import type { CollectiveOffersListStudentLevelsResponseModel } from '../models/CollectiveOffersListStudentLevelsResponseModel';
import type { CollectiveOffersListVenuesResponseModel } from '../models/CollectiveOffersListVenuesResponseModel';
import type { GetPublicCollectiveOfferResponseModel } from '../models/GetPublicCollectiveOfferResponseModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

  /**
   * Récupération de la liste des catégories d'offres proposées.
   * @returns CollectiveOffersListCategoriesResponseModel OK
   * @throws ApiError
   */
  public listCategories(): CancelablePromise<CollectiveOffersListCategoriesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective-offers/categories',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives.
   * @returns CollectiveOffersListDomainsResponseModel OK
   * @throws ApiError
   */
  public listEducationalDomains(): CancelablePromise<CollectiveOffersListDomainsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective-offers/educational-domains',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées.
   * @returns CollectiveOffersListStudentLevelsResponseModel OK
   * @throws ApiError
   */
  public listStudentsLevels(): CancelablePromise<CollectiveOffersListStudentLevelsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective-offers/student-levels',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste des lieux associés à la structure authentifiée par le jeton d'API.
   * Tous les lieux enregistrés, physiques ou virtuels, sont listés ici avec leurs coordonnées.
   * @returns CollectiveOffersListVenuesResponseModel OK
   * @throws ApiError
   */
  public listVenues(): CancelablePromise<CollectiveOffersListVenuesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective-offers/venues',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récuperation de l'offre collective avec l'identifiant offer_id.
   * @param offerId
   * @returns GetPublicCollectiveOfferResponseModel L'offre collective existe
   * @throws ApiError
   */
  public getCollectiveOfferPublic(
    offerId: number,
  ): CancelablePromise<GetPublicCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective-offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour voir cette offre collective`,
        404: `L'offre collective n'existe pas`,
        422: `Unprocessable Entity`,
      },
    });
  }

}
