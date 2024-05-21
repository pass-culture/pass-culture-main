/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetBookingResponse } from '../models/GetBookingResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DPrCiEApiContremarqueService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * @deprecated
   * [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param token
   * @returns void
   * @throws ApiError
   */
  public patchCancelBookingByToken(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/v2/bookings/cancel/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour annuler cette contremarque ou la réservation a déjà été validée`,
        404: `La contremarque n'existe pas`,
        410: `La contremarque a déjà été annulée`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * @deprecated
   * [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param token
   * @returns void
   * @throws ApiError
   */
  public patchBookingKeepByToken(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/v2/bookings/keep/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour voir cette contremarque`,
        404: `La contremarque n'existe pas`,
        410: `La requête est refusée car la contremarque n'a pas encore été validée, a été annulée, ou son remboursement a été initié`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * @deprecated
   * [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param token
   * @returns GetBookingResponse La contremarque existe et n’est pas validée
   * @throws ApiError
   */
  public getBookingByTokenV2(
    token: string,
  ): CancelablePromise<GetBookingResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/v2/bookings/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour voir cette contremarque`,
        404: `La contremarque n'existe pas`,
        410: `Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,
        422: `Unprocessable Entity`,
      },
    });
  }
  /**
   * @deprecated
   * [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param token
   * @returns void
   * @throws ApiError
   */
  public patchBookingUseByToken(
    token: string,
  ): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/v2/bookings/use/token/{token}',
      path: {
        'token': token,
      },
      errors: {
        401: `Authentification nécessaire`,
        403: `Vous n'avez pas les droits nécessaires pour voir cette contremarque`,
        404: `La contremarque n'existe pas`,
        410: `Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,
        422: `Unprocessable Entity`,
      },
    });
  }
}
