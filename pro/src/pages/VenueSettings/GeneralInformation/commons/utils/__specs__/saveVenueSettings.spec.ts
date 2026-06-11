import { apiNew } from '@/apiClient/api'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import { saveVenueSettings } from '../saveVenueSettings'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    editVenue: vi.fn(),
  },
}))

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../../types'

const defaultFormValues: VenueSettingsFormValues = {
  activity: null,
  culturalDomains: [],
  description: 'desc',
  comment: '',
  name: '',
  publicName: '',
  siret: '12345678901234',
  venueSiret: 12345678901234,
  withdrawalDetails:
    "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
  manuallySetAddress: false,
  addressAutocomplete: '123 Rue Principale, Ville Exemple',
  banId: '12345',
  city: 'Ville Exemple',
  latitude: '48.8566',
  longitude: '2.3522',
  coords: '48.8566, 2.3522',
  postalCode: '75001',
  inseeCode: '75111',
  'search-addressAutocomplete': '123 Rue Principale, Ville Exemple',
  street: '123 Rue Principale',
  isOpenToPublic: 'true',
  accessibility: {
    visual: true,
    mental: false,
    audio: false,
    motor: false,
    none: false,
  },
  isAccessibilityAppliedOnAllOffers: false,
}

const defaultFormContext: VenueSettingsFormContext = {
  isCaledonian: false,
  withSiret: true,
  siren: '12345678901234',
  isOpenToPublic: 'true',
}

describe('saveVenueSettings', () => {
  const venue = {
    ...defaultGetVenue,
  }
  const formValues = {
    ...defaultFormValues,
  }

  const formContext: VenueSettingsFormContext = {
    ...defaultFormContext,
  }

  it('should patch venue settings', async () => {
    await saveVenueSettings(formValues, formContext, { venue })

    expect(apiNew.editVenue).toHaveBeenCalledWith({
      path: { venue_id: venue.id },
      body: {
        activity: null,
        banId: '12345',
        city: 'Ville Exemple',
        comment: '',
        culturalDomains: [],
        description: 'desc',
        inseeCode: '75111',
        isManualEdition: false,
        isOpenToPublic: true,
        latitude: 48.8566,
        longitude: 2.3522,
        name: '',
        postalCode: '75001',
        publicName: '',
        siret: '12345678901234',
        street: '123 Rue Principale',
        withdrawalDetails:
          "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
      },
    })
  })
})
