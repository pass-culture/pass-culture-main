import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import { saveVenueSettings } from '../saveVenueSettings'

vi.mock('@/apiClient/api', () => ({
  api: {
    editVenue: vi.fn(),
  },
}))

import { api } from '@/apiClient/api'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../../types'

const defaultFormValues: VenueSettingsFormValues = {
  bookingEmail: 'contact@lieuexemple.com',
  comment: '',
  name: '',
  publicName: '',
  siret: '12345678901234',
  venueSiret: 12345678901234,
  venueType: 'Théâtre',
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
}

const defaultFormContext: VenueSettingsFormContext = {
  isCaledonian: false,
  withSiret: true,
  isVenueVirtual: false,
  siren: '12345678901234',
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

    expect(api.editVenue).toHaveBeenCalledWith(venue.id, {
      banId: '12345',
      bookingEmail: 'contact@lieuexemple.com',
      city: 'Ville Exemple',
      comment: '',
      inseeCode: '75111',
      isManualEdition: false,
      latitude: 48.8566,
      longitude: 2.3522,
      name: '',
      postalCode: '75001',
      publicName: '',
      siret: '12345678901234',
      street: '123 Rue Principale',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })
})
