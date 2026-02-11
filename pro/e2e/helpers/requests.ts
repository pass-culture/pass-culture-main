import type { Response } from 'playwright-core'

export function isGetVenuesReponse(response: Response) {
  return (
    response.url().includes('/venues') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}
export function isGetOffersResponse(response: Response) {
  return (
    response.url().includes('/offers?') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isGetOfferResponse(response: Response) {
  return (
    /\/offers\/\d$/.test(response.url()) &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isPostOfferResponse(response: Response) {
  return (
    response.url().includes('/offers') &&
    response.request().method() === 'POST' &&
    response.status() === 201
  )
}

export function isGetCategoriesResponse(response: Response) {
  return (
    response.url().includes('/offers/categories') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isPatchOffersResponse(response: Response) {
  return (
    response.url().includes('/offers/') &&
    response.request().method() === 'PATCH' &&
    response.status() === 200
  )
}

export function isPutPriceCategoriesResponse(response: Response) {
  return (
    response.url().includes('/price_categories') &&
    response.request().method() === 'PUT' &&
    response.status() === 200
  )
}

export function isPostEventStocksResponse(response: Response) {
  return (
    response.url().includes('/stocks/bulk') &&
    response.request().method() === 'POST' &&
    response.status() === 201
  )
}

export function isPublishOfferResponse(response: Response) {
  return (
    response.url().includes('/offers/publish') &&
    response.request().method() === 'PATCH' &&
    response.status() === 200
  )
}

export function isGetDomainsResponse(response: Response) {
  return (
    response.url().includes('/collective/educational-domains') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isGetInstitutionalRedactorsResponse(response: Response) {
  return (
    response.url().includes('/collective/offers/redactors') &&
    response.request().method() === 'GET'
  )
}

export function isGetCollectiveOffersBookableResponse(response: Response) {
  return (
    response.url().includes('/collective/bookable-offers') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isGetCollectiveOffersTemplateResponse(response: Response) {
  return (
    response.url().includes('/collective/offers-template') &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isGetEligibilityResponse(response: Response) {
  return (
    /\/offerers\/\d\/eligibility/.test(response.url()) &&
    response.request().method() === 'GET' &&
    response.status() === 200
  )
}

export function isPatchStocksResponse(response: Response) {
  return (
    /\/offers\/\d+\/stocks\/$/.test(response.url()) &&
    response.request().method() === 'PATCH' &&
    response.status() === 200
  )
}

export function isPostCollectiveStocksResponse(response: Response) {
  return (
    response.url().includes('/collective/stocks') &&
    response.request().method() === 'POST' &&
    response.status() === 201
  )
}

export function isAdageAddFavoriteResponse(response: Response) {
  return (
    response.url().includes('/adage-iframe/logs/fav-offer') &&
    response.request().method() === 'POST' &&
    response.status() === 204
  )
}

export function isAdageRemoveFavoriteResponse(response: Response) {
  return (
    response.url().includes('/adage-iframe/logs/fav-offer') &&
    response.request().method() === 'POST' &&
    response.status() === 204
  )
}
