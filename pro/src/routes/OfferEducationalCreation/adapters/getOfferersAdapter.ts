import { IUserOfferer, IUserVenue } from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

type Params = null

type IPayload = IUserOfferer[]

type GetOfferersAdapter = Adapter<Params, IPayload>

const FAILING_RESPONSE = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
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
  idAtProviders: null
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
    idAtProviders: string | null
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
    venueTypeId: string
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
      name: venue.publicName,
      address: {
        street: venue.address,
        city: venue.city,
        postalCode: venue.postalCode,
      },
    }))

const serializeOfferers = (offerers: IAPIOfferer[]): IUserOfferer[] =>
  offerers
    .filter(offerer => offerer.isActive && offerer.isValidated)
    .map(offerer => ({
      id: offerer.id,
      name: offerer.name,
      siren: offerer.siren,
      managedVenues: serializeVenues(offerer.managedVenues),
    }))
    .filter(offerer => offerer.managedVenues.length > 0)

const getOfferersAdapter: GetOfferersAdapter = async () => {
  try {
    const result: IAPIOfferer[] = await pcapi.getOfferers()

    return {
      isOk: true,
      message: null,
      payload: serializeOfferers(result),
    }
  } catch (e) {
    return FAILING_RESPONSE
  }
}

export default getOfferersAdapter
