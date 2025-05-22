import { EditVenueBodyModel, VenueTypeCode } from 'apiClient/v1'

import { serializeEditVenueBodyModel } from '../serializers'
import { VenueSettingsFormValues } from '../types'

describe('serializeEditVenueBodyModel', () => {
  let formValues: VenueSettingsFormValues
  let payload: EditVenueBodyModel

  beforeEach(() => {
    formValues = {
      street: '3 Rue de Valois',
      postalCode: '75001',
      inseeCode: '75111',
      city: 'Paris',
      addressAutocomplete: '3 Rue de Valois 75001 Paris',
      'search-addressAutocomplete': '3 Rue de Valois 75001 Paris',
      coords: '48.85332, 2.348979',
      latitude: '48.85332',
      longitude: '2.348979',
      banId: '35288_7283_00001',
      manuallySetAddress: false,
      comment: 'This is a venue comment',
      bookingEmail: 'me@example.com',
      name: 'Lieu de test',
      venueSiret: '',
      publicName: 'Adresse de la venue',
      siret: '418 166 096 00069',
      venueType: 'Centre culturel',
      withdrawalDetails: 'Details for withdraw',
    }

    payload = {
      banId: '35288_7283_00001',
      bookingEmail: 'me@example.com',
      city: 'Paris',
      comment: '',
      latitude: 48.85332,
      longitude: 2.348979,
      name: 'Lieu de test',
      postalCode: '75001',
      inseeCode: '75111',
      publicName: 'Adresse de la venue',
      street: '3 Rue de Valois',
      siret: '41816609600069',
      withdrawalDetails: 'Details for withdraw',
      venueTypeCode: 'Centre culturel' as VenueTypeCode,
      isManualEdition: false,
    }
  })

  it('should serialize form values correctly', () => {
    expect(serializeEditVenueBodyModel(formValues, false)).toEqual(payload)
  })

  it('should not have siret and keep comment if called with "hideSiret"', () => {
    const noSiretPayload = structuredClone(payload)
    delete noSiretPayload.siret

    expect(serializeEditVenueBodyModel(formValues, true)).toEqual({
      ...noSiretPayload,
      comment: 'This is a venue comment',
    })
  })
})
