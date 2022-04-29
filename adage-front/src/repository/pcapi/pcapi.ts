import { Category, Feature, SubCategory } from 'app/types'
import { client } from 'repository/pcapi/pcapiClient'
import { OfferType, Role, VenueFilterType } from 'utils/types'

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

export const getEducationalCategories = async (): Promise<{
  subcategories: SubCategory[]
  categories: Category[]
}> => {
  return client.get('/adage-iframe/offers/categories')
}

export const getFeatures = async (): Promise<Feature[]> =>
  client.get('/adage-iframe/features')
