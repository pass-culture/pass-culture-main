/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GetBookingResponse } from '../models/GetBookingResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class ApiContremarqueService {

  constructor(public readonly httpRequest: BaseHttpRequest) {}

  /**
   * Annulation d'une réservation.
   * Bien que, dans le cas d’un événement, l’utilisateur ne peut plus annuler sa réservation 72h avant le début de ce dernier, cette API permet d’annuler la réservation d’un utilisateur si elle n’a pas encore été validé.
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
   * Annulation de la validation d'une réservation.
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
   * Consultation d'une réservation.
   * Le code “contremarque” ou "token" est une chaîne de caractères permettant d’identifier la réservation et qui sert de preuve de réservation. Ce code unique est généré pour chaque réservation d'un utilisateur sur l'application et lui est transmis à cette occasion.
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
        410: `La contremarque n'est plus valide car elle a déjà été validée ou a été annulée`,
        422: `Unprocessable Entity`,
      },
    });
  }

  /**
   * Validation d'une réservation.
   * Pour confirmer que la réservation a bien été utilisée par le jeune.
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
        410: `La contremarque n'est plus valide car elle a déjà été validée ou a été annulée`,
        422: `Unprocessable Entity`,
      },
    });
  }

}
