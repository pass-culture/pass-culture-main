import { Category, Feature, SubCategory } from 'app/types'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalDomain,
  OfferType,
  VenueFilterType,
} from 'app/types/offers'
import { client } from 'repository/pcapi/pcapiClient'
import { Role } from 'utils/types'

export const authenticate = async (): Promise<Role> => {
  return client
    .get('/adage-iframe/authenticate')
    .then(({ role }: { role: string }) => Role[role])
}

export const getOffer = async (
  offerId: number | string
): Promise<OfferType> => {
  return client.get(`/adage-iframe/offer/${offerId}`)
}

export const getCollectiveOffer = async (
  offerId: number | string
): Promise<CollectiveOffer> =>
  client.get(`/adage-iframe/collective/offers/${offerId}`)

export const getCollectiveOfferTemplate = async (
  offerId: number | string
): Promise<CollectiveOfferTemplate> =>
  client.get(`/adage-iframe/collective/offers-template/${offerId}`)

export const getVenueBySiret = async (
  siret: string
): Promise<VenueFilterType> => {
  return client.get(`/adage-iframe/venues/siret/${siret}`)
}

export const getVenueById = async (
  venueId: string
): Promise<VenueFilterType> => {
  return client.get(`/adage-iframe/venues/${venueId}`)
}

export const preBookStock = async (stockId: number): Promise<number> => {
  return client.post('/adage-iframe/bookings', { stockId })
}

export const preBookCollectiveStock = async (
  stockId: number
): Promise<number> => {
  return client.post('/adage-iframe/collective/bookings', { stockId })
}

export const getEducationalCategories = async (): Promise<{
  subcategories: SubCategory[]
  categories: Category[]
}> => {
  return client.get('/adage-iframe/offers/categories')
}

export const getFeatures = async (): Promise<Feature[]> =>
  client.get('/adage-iframe/features')

export const getEducationalDomains = async (): Promise<EducationalDomain[]> =>
  client.get('/collective/educational-domains')
