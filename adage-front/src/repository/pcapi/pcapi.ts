import { Feature } from 'app/types'
import { EducationalDomain } from 'app/types/offers'
import { client } from 'repository/pcapi/pcapiClient'

export const preBookStock = async (stockId: number): Promise<number> => {
  return client.post('/adage-iframe/bookings', { stockId })
}

export const getFeatures = async (): Promise<Feature[]> =>
  client.get('/adage-iframe/features')

export const getEducationalDomains = async (): Promise<EducationalDomain[]> =>
  client.get('/collective/educational-domains')

export const logCatalogView = async (): Promise<null> => {
  return client.post('/adage-iframe/logs/catalog-view', {})
}

export const logSearchButton = async (): Promise<null> => {
  return client.post('/adage-iframe/logs/search-button', {})
}

export const logOfferDetail = async (stockId: number): Promise<null> => {
  return client.post('/adage-iframe/logs/offer-detail', { stockId: stockId })
}

export const logBookingModalButton = async (stockId: number): Promise<null> => {
  return client.post('/adage-iframe/logs/booking-modal-button', {
    stockId: stockId,
  })
}
