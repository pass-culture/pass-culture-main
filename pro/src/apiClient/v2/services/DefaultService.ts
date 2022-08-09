/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectiveOffersListVenuesResponseModel } from '../models/CollectiveOffersListVenuesResponseModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
