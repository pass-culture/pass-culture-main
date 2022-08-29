/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOffersListCategoriesResponseModel } from '../models/CollectiveOffersListCategoriesResponseModel';
import type { CollectiveOffersListDomainsResponseModel } from '../models/CollectiveOffersListDomainsResponseModel';
import type { CollectiveOffersListEducationalInstitutionResponseModel } from '../models/CollectiveOffersListEducationalInstitutionResponseModel';
import type { CollectiveOffersListResponseModel } from '../models/CollectiveOffersListResponseModel';
import type { CollectiveOffersListStudentLevelsResponseModel } from '../models/CollectiveOffersListStudentLevelsResponseModel';
import type { CollectiveOffersListVenuesResponseModel } from '../models/CollectiveOffersListVenuesResponseModel';
import type { GetPublicCollectiveOfferResponseModel } from '../models/GetPublicCollectiveOfferResponseModel';
import type { OfferStatus } from '../models/OfferStatus';
import type { PatchCollectiveOfferBodyModel } from '../models/PatchCollectiveOfferBodyModel';
import type { PostCollectiveOfferBodyModel } from '../models/PostCollectiveOfferBodyModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ApiOffresCollectivesService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

  /**
   * Récupération de la liste des catégories d'offres proposées.
   * @returns CollectiveOffersListCategoriesResponseModel La liste des catégories éligibles existantes.
   * @throws ApiError
   */
  public listCategories(): CancelablePromise<CollectiveOffersListCategoriesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/categories',
      errors: {
        401: `Authentification nécessaire`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste des domaines d'éducation pouvant être associés aux offres collectives.
   * @returns CollectiveOffersListDomainsResponseModel La liste des domaines d'éducation.
   * @throws ApiError
   */
  public listEducationalDomains(): CancelablePromise<CollectiveOffersListDomainsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/educational-domains',
      errors: {
        401: `Authentification nécessaire`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste établissements scolaires.
   * @param id
   * @param name
   * @param institutionType
   * @param city
   * @param postalCode
   * @param limit
   * @returns CollectiveOffersListEducationalInstitutionResponseModel La liste des établissement scolaires éligibles.
   * @throws ApiError
   */
  public listEducationalInstitutions(
    id?: number | null,
    name?: string | null,
    institutionType?: string | null,
    city?: string | null,
    postalCode?: string | null,
    limit: number = 20,
  ): CancelablePromise<CollectiveOffersListEducationalInstitutionResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/educational-institutions/',
      query: {
        'id': id,
        'name': name,
        'institutionType': institutionType,
        'city': city,
        'postalCode': postalCode,
        'limit': limit,
      },
      errors: {
        400: `Requête malformée`,
        401: `Authentification nécessaire`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récuperation de l'offre collective avec l'identifiant offer_id. Cette api ignore les offre vitrines et les offres commencées sur l'interface web et non finalisées.
   * @param status
   * @param venueId
   * @param periodBeginningDate
   * @param periodEndingDate
   * @returns CollectiveOffersListResponseModel L'offre collective existe
   * @throws ApiError
   */
  public getCollectiveOffersPublic(
    status?: OfferStatus | null,
    venueId?: number | null,
    periodBeginningDate?: string | null,
    periodEndingDate?: string | null,
  ): CancelablePromise<CollectiveOffersListResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/offers/',
      query: {
        'status': status,
        'venueId': venueId,
        'periodBeginningDate': periodBeginningDate,
        'periodEndingDate': periodEndingDate,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour voir cette offre collective`,
        404: `L'offre collective n'existe pas`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Création d'une offre collective.
   * @param requestBody
   * @returns GetPublicCollectiveOfferResponseModel L'offre collective à été créée avec succes
   * @throws ApiError
   */
  public postCollectiveOfferPublic(
    requestBody?: PostCollectiveOfferBodyModel,
  ): CancelablePromise<GetPublicCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/v2/collective/offers/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Requête malformée`,
        401: `Authentification nécessaire`,
        403: `Non éligible pour les offres collectives`,
        404: `L'une des resources pour la création de l'offre n'a pas été trouvée`,
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
      url: '/v2/collective/offers/{offer_id}',
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

  /**
   * Édition d'une offre collective.
   * @param offerId
   * @param requestBody
   * @returns GetPublicCollectiveOfferResponseModel L'offre collective à été édité avec succes
   * @throws ApiError
   */
  public patchCollectiveOfferPublic(
    offerId: number,
    requestBody?: PatchCollectiveOfferBodyModel,
  ): CancelablePromise<GetPublicCollectiveOfferResponseModel> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/v2/collective/offers/{offer_id}',
      path: {
        'offer_id': offerId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        400: `Requête malformée`,
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour éditer cette offre collective`,
        404: `L'une des resources pour la création de l'offre n'a pas été trouvée`,
        422: `Cetains champs ne peuvent pas être édités selon l'état de l'offre`,
      },
    });
  }

  /**
   * Récupération de la liste des publics cibles pour lesquelles des offres collectives peuvent être proposées.
   * @returns CollectiveOffersListStudentLevelsResponseModel La liste des domaines d'éducation.
   * @throws ApiError
   */
  public listStudentsLevels(): CancelablePromise<CollectiveOffersListStudentLevelsResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/student-levels',
      errors: {
        401: `Authentification nécessaire`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Récupération de la liste des lieux associés à la structure authentifiée par le jeton d'API.
   * Tous les lieux enregistrés, sont listés ici avec leurs coordonnées.
   * @returns CollectiveOffersListVenuesResponseModel La liste des lieux ou vous pouvez créer une offre.
   * @throws ApiError
   */
  public listVenues(): CancelablePromise<CollectiveOffersListVenuesResponseModel> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/collective/venues',
      errors: {
        401: `Authentification nécessaire`,
        422: `Unprocessable Entity`,
      },
    });
  }

}
