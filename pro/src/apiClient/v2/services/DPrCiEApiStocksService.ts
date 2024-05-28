/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UpdateVenueStocksBodyModel } from '../models/UpdateVenueStocksBodyModel';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DPrCiEApiStocksService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * @deprecated
   * update_stocks <POST>
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
