import { Feature } from 'app/types'
import { EducationalDomain, OfferType } from 'app/types/offers'
import { client } from 'repository/pcapi/pcapiClient'

export const getOffer = async (
  offerId: number | string
): Promise<OfferType> => {
  return client.get(`/adage-iframe/offer/${offerId}`)
}

export const preBookStock = async (stockId: number): Promise<number> => {
  return client.post('/adage-iframe/bookings', { stockId })
}

export const preBookCollectiveStock = async (
  stockId: number
): Promise<number> => {
  return client.post('/adage-iframe/collective/bookings', { stockId })
}

export const getFeatures = async (): Promise<Feature[]> =>
  client.get('/adage-iframe/features')

export const getEducationalDomains = async (): Promise<EducationalDomain[]> =>
  client.get('/collective/educational-domains')
