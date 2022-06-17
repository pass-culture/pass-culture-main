import { Fetcher } from 'openapi-typescript-fetch'
import { paths } from './schema'

// declare fetcher for paths
const fetcher = Fetcher.for<paths>()

// global configuration
fetcher.configure({
  baseUrl: 'https://petstore.swagger.io/v2',
  init: {
    headers: {},
  },
})

// create fetch operations
export const getIndividualBookings = fetcher
  .path('/bookings/pro')
  .method('get')
  .create()

export const getCollectiveBookings = fetcher
  .path('/collective/bookings/pro')
  .method('get')
  .create()

export const getCollectiveOffers = fetcher
  .path('/collective/offers')
  .method('get')
  .create()

export const postCollectiveOffer = fetcher
  .path('/collective/offers')
  .method('post')
  .create()

export const patchCollectiveOfferTemplateActiveStatus = fetcher
  .path('/collective/offers-template/active-status')
  .method('patch')
  .create()

export const getCollectiveOfferTemplate = fetcher
  .path('/collective/offers-template/{offer_id}')
  .method('get')
  .create()

export const patchCollectiveOfferTemplate = fetcher
  .path('/collective/offers-template/{offer_id}')
  .method('patch')
  .create()

export const postCollectiveOfferTemplate = fetcher
  .path('/collective/offers-template/{offer_id}/')
  .method('post')
  .create()

export const patchCollectiveOfferActiveStatus = fetcher
  .path('/collective/offers/active-status')
  .method('patch')
  .create()

export const patchAllCollectiveOfferActiveStatus = fetcher
  .path('/collective/offers/all-active-status')
  .method('patch')
  .create()

export const getCollectiveOffer = fetcher
  .path('/collective/offers/{offer_id}')
  .method('get')
  .create()

export const patchCollectiveOffer = fetcher
  .path('/collective/offers/{offer_id}')
  .method('patch')
  .create()

export const cancelCollectiveOfferBooking = fetcher
  .path('/collective/offers/{offer_id}/cancel_booking')
  .method('patch')
  .create()

export const updateCollectiveOfferInstitution = fetcher
  .path('/collective/offers/{offer_id}/educational_institution')
  .method('patch')
  .create()

export const getCollectiveOfferStock = fetcher
  .path('/collective/offers/{offer_id}/stock')
  .method('get')
  .create()

export const postCollectiveStock = fetcher
  .path('/collective/stocks')
  .method('post')
  .create()

export const patchCollectiveStock = fetcher
  .path('/collective/stocks/{collective_stock_id}')
  .method('patch')
  .create()

export const getEducationalInstitutions = fetcher
  .path('/educational_institutions')
  .method('get')
  .create()

export const getFeatures = fetcher.path('/features').method('get').create()

export const getBusinessUnits = fetcher
  .path('/finance/business-units')
  .method('get')
  .create()

export const patchBusinessUnit = fetcher
  .path('/finance/business-units/{business_unit_id}')
  .method('patch')
  .create()

export const getInvoices = fetcher
  .path('/finance/invoices')
  .method('get')
  .create()

export const getOfferers = fetcher.path('/offerers').method('get').create()

export const postOfferers = fetcher.path('/offerers').method('post').create()

export const deleteApiKey = fetcher
  .path('/offerers/api_keys/{api_key_prefix}')
  .method('delete')
  .create()

export const getEducationalOfferers = fetcher
  .path('/offerers/educational')
  .method('get')
  .create()

export const getOfferersNames = fetcher
  .path('/offerers/names')
  .method('get')
  .create()

export const getOffererEACEligibility = fetcher
  .path('/offerers/{humanized_offerer_id}/eac-eligibility')
  .method('get')
  .create()

export const getOfferer = fetcher
  .path('/offerers/{offerer_id}')
  .method('get')
  .create()

export const postApiKey = fetcher
  .path('/offerers/{offerer_id}/api_keys')
  .method('post')
  .create()

export const getOffers = fetcher.path('/offers').method('get').create()

export const postOffer = fetcher.path('/offers').method('post').create()

export const patchOfferActiveStatus = fetcher
  .path('/offers/active-status')
  .method('patch')
  .create()

export const patchAllOfferActiveStatus = fetcher
  .path('/offers/all-active-status')
  .method('patch')
  .create()

export const getCategories = fetcher
  .path('/offers/categories')
  .method('get')
  .create()

export const postEducationalOffer = fetcher
  .path('/offers/educational')
  .method('post')
  .create()

export const patchEducationalOffer = fetcher
  .path('/offers/educational/{offer_id}')
  .method('patch')
  .create()

export const postOfferThumbnail = fetcher
  .path('/offers/thumbnails/')
  .method('post')
  .create()

export const getOffer = fetcher
  .path('/offers/{offer_id}')
  .method('get')
  .create()

export const patchOffer = fetcher
  .path('/offers/{offer_id}')
  .method('patch')
  .create()

export const cancelOfferBooking = fetcher
  .path('/offers/{offer_id}/cancel_booking')
  .method('patch')
  .create()

export const getOfferStocks = fetcher
  .path('/offers/{offer_id}/stocks')
  .method('get')
  .create()

export const getReimbursementsCsv = fetcher
  .path('/reimbursements/csv')
  .method('get')
  .create()

export const postStockBulk = fetcher
  .path('/stocks/bulk')
  .method('post')
  .create()

export const postEducationalStock = fetcher
  .path('/stocks/educational')
  .method('post')
  .create()

export const patchEducationalStock = fetcher
  .path('/stocks/educational/{stock_id}')
  .method('patch')
  .create()

export const deleteStock = fetcher
  .path('/stocks/{stock_id}')
  .method('delete')
  .create()

export const getCurrentUser = fetcher
  .path('/users/current')
  .method('get')
  .create()

export const patchCurrentUser = fetcher
  .path('/users/current')
  .method('patch')
  .create()

export const patchUserHasSeenRGS = fetcher
  .path('/users/rgs-seen')
  .method('patch')
  .create()

export const signin = fetcher.path('/users/signin').method('post').create()

export const getUserToken = fetcher
  .path('/users/token/{token}')
  .method('get')
  .create()

export const patchUserHasSeenTuto = fetcher
  .path('/users/tuto-seen')
  .method('patch')
  .create()

export const validateUserToken = fetcher
  .path('/validate/user/{token}')
  .method('patch')
  .create()

export const getVenuesLabels = fetcher
  .path('/venue-labels')
  .method('get')
  .create()

export const getVenueTypes = fetcher.path('/venue-types').method('get').create()

export const getVenueProviders = fetcher
  .path('/venueProviders')
  .method('get')
  .create()

export const postVenueProviders = fetcher
  .path('/venueProviders')
  .method('post')
  .create()

export const putVenueProviders = fetcher
  .path('/venueProviders')
  .method('put')
  .create()

export const getVenueStats = fetcher
  .path('/venues/{humanized_venue_id}/stats')
  .method('get')
  .create()

export const getVenue = fetcher
  .path('/venues/{venue_id}')
  .method('get')
  .create()

export const patchVenue = fetcher
  .path('/venues/{venue_id}')
  .method('patch')
  .create()
