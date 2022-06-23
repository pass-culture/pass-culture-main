/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UpdateVenueStocksBodyModel } from '../models/UpdateVenueStocksBodyModel';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ApiStocksService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

  /**
   * Mise à jour des stocks d'un lieu enregistré auprès du pass Culture.
   * Seuls les livres, préalablement présents dans le catalogue du pass Culture seront pris en compte, tous les autres stocks seront filtrés. Les stocks sont référencés par leur isbn au format EAN13. Le champ "available" représente la quantité de stocks disponible en librairie. Le champ "price" (optionnel) correspond au prix en euros. Le paramètre {venue_id} correspond à un lieu qui doit être attaché à la structure à laquelle la clé d'API utilisée est reliée.
   * @param venueId
   * @param requestBody
   * @returns void
   * @throws ApiError
   */
  public updateStocks(
    venueId: number,
    requestBody?: UpdateVenueStocksBodyModel,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/v2/venue/{venue_id}/stocks',
      path: {
        'venue_id': venueId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        404: `Not Found`,
        422: `Unprocessable Entity`,
      },
    });
  }

}
