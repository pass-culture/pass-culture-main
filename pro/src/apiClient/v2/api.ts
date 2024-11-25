/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import { OpenAPIConfig } from 'apiClient/core/OpenAPI'
import { request } from 'apiClient/customRequest'
import { ApiRequestOptions } from 'apiClient/core/ApiRequestOptions'
import { CancelablePromise } from 'apiClient/core/CancelablePromise'

/**
 *
 * @export
 */
export const COLLECTION_FORMATS = {
  csv: ',',
  ssv: ' ',
  tsv: '\t',
  pipes: '|',
}

/**
 *
 * @export
 * @class BaseAPI
 */
export class BaseAPI {
  protected configuration: OpenAPIConfig

  constructor(configuration: OpenAPIConfig) {
    this.configuration = configuration
  }
}

/**
 *
 * @export
 * @class RequiredError
 * @extends {Error}
 */
export class RequiredError extends Error {
  name = 'RequiredError'
  constructor(public field: string, msg?: string) {
    super(msg)
  }
}

/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BookingFormula {
  PLACE = <any> 'PLACE',
  ABO = <any> 'ABO'
}
/**
 * An enumeration.
 * @export
 * @enum {string}
 */
export enum BookingOfferType {
  BIEN = <any> 'BIEN',
  EVENEMENT = <any> 'EVENEMENT'
}
/**
 * 
 * @export
 * @interface GetBookingResponse
 */
export interface GetBookingResponse {
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  bookingId: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  dateOfBirth?: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  datetime: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  ean13?: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  email: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  firstName?: string
  /**
   * S'applique uniquement aux offres de catégorie Cinéma. Abonnement (ABO) ou place (PLACE).
   * @type {BookingFormula}
   * @memberof GetBookingResponse
   */
  formula?: BookingFormula
  /**
   * 
   * @type {boolean}
   * @memberof GetBookingResponse
   */
  isUsed: boolean
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  lastName?: string
  /**
   * 
   * @type {number}
   * @memberof GetBookingResponse
   */
  offerId: number
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  offerName: string
  /**
   * 
   * @type {BookingOfferType}
   * @memberof GetBookingResponse
   */
  offerType: BookingOfferType
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  phoneNumber?: string
  /**
   * 
   * @type {number}
   * @memberof GetBookingResponse
   */
  price: number
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  priceCategoryLabel?: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  publicOfferId: string
  /**
   * 
   * @type {number}
   * @memberof GetBookingResponse
   */
  quantity: number
  /**
   * Identifiant du film et de la salle dans le cas d’une offre synchronisée par Allociné.
   * @type {any}
   * @memberof GetBookingResponse
   */
  theater: any
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  userName: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  venueAddress?: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  venueDepartmentCode?: string
  /**
   * 
   * @type {string}
   * @memberof GetBookingResponse
   */
  venueName: string
}
/**
 * Available stock quantity for a book
 * @export
 * @interface UpdateVenueStockBodyModel
 */
export interface UpdateVenueStockBodyModel {
  /**
   * 
   * @type {number}
   * @memberof UpdateVenueStockBodyModel
   */
  available: number
  /**
   * 
   * @type {number}
   * @memberof UpdateVenueStockBodyModel
   */
  price: number
  /**
   * Format: EAN13
   * @type {string}
   * @memberof UpdateVenueStockBodyModel
   */
  ref: string
}
/**
 * 
 * @export
 * @interface UpdateVenueStocksBodyModel
 */
export interface UpdateVenueStocksBodyModel {
  /**
   * 
   * @type {Array<UpdateVenueStockBodyModel>}
   * @memberof UpdateVenueStocksBodyModel
   */
  stocks: Array<UpdateVenueStockBodyModel>
}
/**
 * Model of a validation error response.
 * @export
 */
export type ValidationError = Array<ValidationErrorElement>
/**
 * Model of a validation error response element.
 * @export
 * @interface ValidationErrorElement
 */
export interface ValidationErrorElement {
  /**
   * 
   * @type {any}
   * @memberof ValidationErrorElement
   */
  ctx?: any
  /**
   * 
   * @type {Array<string>}
   * @memberof ValidationErrorElement
   */
  loc: Array<string>
  /**
   * 
   * @type {string}
   * @memberof ValidationErrorElement
   */
  msg: string
  /**
   * 
   * @type {string}
   * @memberof ValidationErrorElement
   */
  type: string
}
/**
 * DprcieAPIContremarqueApi - fetch parameter creator
 * @export
 */
export const DprcieAPIContremarqueApiFetchParamCreator = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingByTokenV2(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling getBookingByTokenV2.')
      }
      const localVarPath = `/v2/bookings/token/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'GET', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication ApiKeyAuth required

      // authentication SessionAuth required
      if (configuration && configuration.apiKey) {
        const localVarApiKeyValue = typeof configuration.apiKey === 'function'
					? configuration.apiKey('session')
					: configuration.apiKey
        localVarQueryParameter['session'] = localVarApiKeyValue
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingKeepByToken(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling patchBookingKeepByToken.')
      }
      const localVarPath = `/v2/bookings/keep/token/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication ApiKeyAuth required

      // authentication SessionAuth required
      if (configuration && configuration.apiKey) {
        const localVarApiKeyValue = typeof configuration.apiKey === 'function'
					? configuration.apiKey('session')
					: configuration.apiKey
        localVarQueryParameter['session'] = localVarApiKeyValue
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingUseByToken(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling patchBookingUseByToken.')
      }
      const localVarPath = `/v2/bookings/use/token/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication ApiKeyAuth required

      // authentication SessionAuth required
      if (configuration && configuration.apiKey) {
        const localVarApiKeyValue = typeof configuration.apiKey === 'function'
					? configuration.apiKey('session')
					: configuration.apiKey
        localVarQueryParameter['session'] = localVarApiKeyValue
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCancelBookingByToken(token: string, options: any = {}): ApiRequestOptions {
      // verify required parameter 'token' is not null or undefined
      if (token === null || token === undefined) {
        throw new RequiredError('token','Required parameter token was null or undefined when calling patchCancelBookingByToken.')
      }
      const localVarPath = `/v2/bookings/cancel/token/{token}`
        .replace(`{${'token'}}`, encodeURIComponent(String(token)))
      const localVarRequestOptions = Object.assign({ method: 'PATCH', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any
      const localVarQueryParameter = {} as any


      // authentication ApiKeyAuth required

      // authentication SessionAuth required
      if (configuration && configuration.apiKey) {
        const localVarApiKeyValue = typeof configuration.apiKey === 'function'
					? configuration.apiKey('session')
					: configuration.apiKey
        localVarQueryParameter['session'] = localVarApiKeyValue
      }

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)

      return localVarRequestOptions
    },
  }
}

/**
 * DprcieAPIContremarqueApi - functional programming interface
 * @export
 */
export const DprcieAPIContremarqueApiFp = function(configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingByTokenV2(token: string, options?: any): CancelablePromise<GetBookingResponse> {
      const localVarApiRequestOptions = DprcieAPIContremarqueApiFetchParamCreator(configuration).getBookingByTokenV2(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingKeepByToken(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DprcieAPIContremarqueApiFetchParamCreator(configuration).patchBookingKeepByToken(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingUseByToken(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DprcieAPIContremarqueApiFetchParamCreator(configuration).patchBookingUseByToken(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCancelBookingByToken(token: string, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DprcieAPIContremarqueApiFetchParamCreator(configuration).patchCancelBookingByToken(token, options)
      return request(configuration, localVarApiRequestOptions)
    },
  }
}

/**
 * DprcieAPIContremarqueApi - factory interface
 * @export
 */
export const DprcieAPIContremarqueApiFactory = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    getBookingByTokenV2(token: string, options?: any) {
      return DprcieAPIContremarqueApiFp(configuration).getBookingByTokenV2(token, options)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingKeepByToken(token: string, options?: any) {
      return DprcieAPIContremarqueApiFp(configuration).patchBookingKeepByToken(token, options)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchBookingUseByToken(token: string, options?: any) {
      return DprcieAPIContremarqueApiFp(configuration).patchBookingUseByToken(token, options)
    },
    /**
     * 
     * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
     * @param {string} token 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    patchCancelBookingByToken(token: string, options?: any) {
      return DprcieAPIContremarqueApiFp(configuration).patchCancelBookingByToken(token, options)
    },
  }
}

/**
 * DprcieAPIContremarqueApi - object-oriented interface
 * @export
 * @class DprcieAPIContremarqueApi
 * @extends {BaseAPI}
 */
export class DprcieAPIContremarqueApi extends BaseAPI {
  /**
   * 
   * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DprcieAPIContremarqueApi
   */
  public getBookingByTokenV2(token: string, options?: any) {
    return DprcieAPIContremarqueApiFp(this.configuration).getBookingByTokenV2(token, options)
  }

  /**
   * 
   * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DprcieAPIContremarqueApi
   */
  public patchBookingKeepByToken(token: string, options?: any) {
    return DprcieAPIContremarqueApiFp(this.configuration).patchBookingKeepByToken(token, options)
  }

  /**
   * 
   * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DprcieAPIContremarqueApi
   */
  public patchBookingUseByToken(token: string, options?: any) {
    return DprcieAPIContremarqueApiFp(this.configuration).patchBookingUseByToken(token, options)
  }

  /**
   * 
   * @summary [Dépréciée] Contactez partenaires.techniques@passculture.app pour plus d'informations.
   * @param {string} token 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DprcieAPIContremarqueApi
   */
  public patchCancelBookingByToken(token: string, options?: any) {
    return DprcieAPIContremarqueApiFp(this.configuration).patchCancelBookingByToken(token, options)
  }

}
/**
 * DprcieAPIStocksApi - fetch parameter creator
 * @export
 */
export const DprcieAPIStocksApiFetchParamCreator = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary update_stocks <POST>
     * @param {number} venue_id 
     * @param {UpdateVenueStocksBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateStocks(venue_id: number, body?: UpdateVenueStocksBodyModel, options: any = {}): ApiRequestOptions {
      // verify required parameter 'venue_id' is not null or undefined
      if (venue_id === null || venue_id === undefined) {
        throw new RequiredError('venue_id','Required parameter venue_id was null or undefined when calling updateStocks.')
      }
      const localVarPath = `/v2/venue/{venue_id}/stocks`
        .replace(`{${'venue_id'}}`, encodeURIComponent(String(venue_id)))
      const localVarRequestOptions = Object.assign({ method: 'POST', url: localVarPath }, options)
      const localVarHeaderParameter = {} as any


      // authentication ApiKeyAuth required

      localVarHeaderParameter['Content-Type'] = 'application/json'

      localVarRequestOptions.headers = Object.assign({}, localVarHeaderParameter, options.headers)
      localVarRequestOptions.body =  body || ''

      return localVarRequestOptions
    },
  }
}

/**
 * DprcieAPIStocksApi - functional programming interface
 * @export
 */
export const DprcieAPIStocksApiFp = function(configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary update_stocks <POST>
     * @param {number} venue_id 
     * @param {UpdateVenueStocksBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateStocks(venue_id: number, body?: UpdateVenueStocksBodyModel, options?: any): CancelablePromise<Response> {
      const localVarApiRequestOptions = DprcieAPIStocksApiFetchParamCreator(configuration).updateStocks(venue_id, body, options)
      return request(configuration, localVarApiRequestOptions)
    },
  }
}

/**
 * DprcieAPIStocksApi - factory interface
 * @export
 */
export const DprcieAPIStocksApiFactory = function (configuration: OpenAPIConfig) {
  return {
    /**
     * 
     * @summary update_stocks <POST>
     * @param {number} venue_id 
     * @param {UpdateVenueStocksBodyModel} [body] 
     * @param {*} [options] Override http request option.
     * @throws {RequiredError}
     */
    updateStocks(venue_id: number, body?: UpdateVenueStocksBodyModel, options?: any) {
      return DprcieAPIStocksApiFp(configuration).updateStocks(venue_id, body, options)
    },
  }
}

/**
 * DprcieAPIStocksApi - object-oriented interface
 * @export
 * @class DprcieAPIStocksApi
 * @extends {BaseAPI}
 */
export class DprcieAPIStocksApi extends BaseAPI {
  /**
   * 
   * @summary update_stocks <POST>
   * @param {number} venue_id 
   * @param {UpdateVenueStocksBodyModel} [body] 
   * @param {*} [options] Override http request option.
   * @throws {RequiredError}
   * @memberof DprcieAPIStocksApi
   */
  public updateStocks(venue_id: number, body?: UpdateVenueStocksBodyModel, options?: any) {
    return DprcieAPIStocksApiFp(this.configuration).updateStocks(venue_id, body, options)
  }

}
