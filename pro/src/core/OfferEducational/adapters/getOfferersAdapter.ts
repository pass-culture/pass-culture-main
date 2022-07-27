import { IUserOfferer, IUserVenue } from 'core/OfferEducational'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = string | null

type IPayload = IUserOfferer[]

type GetOfferersAdapter = Adapter<Params, IPayload, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

// TODO move and clarify this when pcapi is finaly typed
type IAPIOfferer = {
  address: string
  bic: string
  city: string
  dateCreated: string
  dateModifiedAtLastProvider: string
  dateValidated: string | null
  demarchesSimplifieesApplicationId: number
  fieldsUpdated: []
  iban: string
  id: string
  isActive: boolean
  isValidated: boolean
  lastProviderId: string | null
  managedVenues: {
    address: string
    audioDisabilityCompliant: boolean
    bannerMeta: string | null
    bannerUrl: string | null
    bic: string
    bookingEmail: string
    businessUnitId: string
    city: string
    comment: null
    dateCreated: string
    dateModifiedAtLastProvider: string
    departementCode: string
    description: string
    fieldsUpdated: []
    iban: string
    id: string
    isPermanent: true
    isVirtual: boolean
    lastProviderId: null
    latitude: number
    longitude: number
    managingOffererId: string
    mentalDisabilityCompliant: boolean
    motorDisabilityCompliant: boolean
    nOffers: number
    name: string
    postalCode: string
    publicName: string
    siret: string
    thumbCount: number
    venueLabelId: string | null
    venueTypeCode: string
    visualDisabilityCompliant: boolean
    withdrawalDetails: null
  }[]
  nOffers: number
  name: string
  postalCode: string
  siren: string
  thumbCount: number
  userHasAccess: boolean
}

const serializeVenues = (venues: IAPIOfferer['managedVenues']): IUserVenue[] =>
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

const serializeOfferers = (offerers: IAPIOfferer[]): IUserOfferer[] =>
  offerers.map(offerer => ({
    id: offerer.id,
    name: offerer.name,
    managedVenues: serializeVenues(offerer.managedVenues),
  }))

export const getOfferersAdapter: GetOfferersAdapter = async (
  offererId: string | null
) => {
  try {
    const { educationalOfferers }: { educationalOfferers: IAPIOfferer[] } =
      await pcapi.getEducationalOfferers(offererId)

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
