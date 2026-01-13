/* istanbul ignore file */
import merge from 'lodash/merge'

import type {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
  LocationBodyModel,
  StructureDataBodyModel,
} from '@/apiClient/v1'

let venueId = 1

export const managedVenueFactory = (
  userVenueExtends: Partial<GetEducationalOffererVenueResponseModel> = {}
): GetEducationalOffererVenueResponseModel => {
  const currentVenueId = venueId++
  return merge(
    {},
    {
      id: currentVenueId,
      name: 'Nom de la structure',
      publicName: 'Nom public de la structure',
      address: '2 bis Street Name',
      postalCode: '93100',
      city: 'Montreuil',
      isVirtual: false,
    },
    userVenueExtends
  )
}

export const managedVenuesFactory = (
  managedVenuesExtends: Partial<GetEducationalOffererVenueResponseModel>[]
): GetEducationalOffererVenueResponseModel[] =>
  managedVenuesExtends.map(managedVenueFactory)

let offererId = 1

export const userOffererFactory = (
  userOffererExtends: Partial<GetEducationalOffererResponseModel> = {}
): GetEducationalOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    id: currentOffererId,
    name: 'offerer name',
    allowedOnAdage: true,
    managedVenues: [managedVenueFactory({})],
    ...userOffererExtends,
  }
}

export const structureDataBodyModelFactory = (
  overrides: Partial<StructureDataBodyModel> = {}
): StructureDataBodyModel => {
  return {
    location: locationBodyModelFactory(overrides.location ?? {}),
    apeCode: '9003A',
    isDiffusible: true,
    name: 'ma super stucture',
    siren: '123456789',
    siret: '12345678933333',
    ...overrides,
  }
}

const locationBodyModelFactory = (
  overrides: Partial<LocationBodyModel> = {}
): LocationBodyModel => {
  return {
    banId: '49759_1304_00002',
    city: 'Paris',
    inseeCode: '75056',
    isManualEdition: false,
    isVenueLocation: true,
    label: 'Ma super maison',
    latitude: 48.869440910282734,
    longitude: 2.3087717501609233,
    postalCode: '75001',
    street: '4 rue Carnot',
    ...overrides,
  }
}
