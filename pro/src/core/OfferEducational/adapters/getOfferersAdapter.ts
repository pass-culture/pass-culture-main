import { IUserOfferer, IUserVenue } from 'core/OfferEducational'
import { EducationalOfferer } from 'custom_types'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = string | null

type IPayload = IUserOfferer[]

type GetOfferersAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: [],
}

const serializeVenues = (
  venues: EducationalOfferer['managedVenues']
): IUserVenue[] =>
  venues
    .filter(venue => !venue.isVirtual)
    .map(venue => ({
      id: venue.id,
      name: venue.publicName || venue.name,
      address: {
        street: venue.address,
        city: venue.city,
        postalCode: venue.postalCode,
      },
    }))

const serializeOfferers = (offerers: EducationalOfferer[]): IUserOfferer[] =>
  offerers.map(offerer => ({
    id: offerer.id,
    name: offerer.name,
    managedVenues: serializeVenues(offerer.managedVenues),
  }))

export const getOfferersAdapter: GetOfferersAdapter = async (
  offererId: string | null
) => {
  if (!offererId) {
    return FAILING_RESPONSE
  }

  try {
    const { educationalOfferers } = await pcapi.getEducationalOfferers(
      offererId
    )

    return {
      isOk: true,
      message: null,
      payload: serializeOfferers(educationalOfferers),
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOfferersAdapter
