import { GetVenueResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'commons/utils/collectiveApiFactories'

import { setInitialFormValues } from '../setInitialFormValues'

let venue: GetVenueResponseModel

describe('setInitialFormValues', () => {
  beforeEach(() => {
    venue = {
      ...defaultGetVenue,
      publicName: 'Adresse de la venue',
      street: '3 Rue de Valois',
      postalCode: '75001',
      city: 'Paris',
      latitude: 48.85332,
      longitude: 2.348979,
      banId: '35288_7283_00001',
    }
  })

  it('should return a valid initial form object', () => {
    const formValues = setInitialFormValues({
      venue,
    })

    const expectedFormValues = {
      street: '3 Rue de Valois',
      postalCode: '75001',
      city: 'Paris',
      addressAutocomplete: '3 Rue de Valois 75001 Paris',
      'search-addressAutocomplete': '3 Rue de Valois 75001 Paris',
      coords: '48.85332, 2.348979',
      latitude: '48.85332',
      longitude: '2.348979',
      banId: '35288_7283_00001',
      manuallySetAddress: undefined,
      comment: '',
      bookingEmail: '',
      name: 'Lieu de test',
      venueSiret: null,
      publicName: 'Adresse de la venue',
      siret: '',
      venueLabel: '',
      venueType: 'Centre culturel',
      withdrawalDetails: '',
      isWithdrawalAppliedOnAllOffers: false,
    }

    expect(formValues).toEqual(expectedFormValues)
  })

  it('should return a valid initial form object with offer address fields', () => {
    const formValues = setInitialFormValues({
      venue: {
        ...venue,
        address: {
          id: 978,
          id_oa: 1012,
          city: 'Montpellier',
          street: '79 Quai du Palladium',
          postalCode: '34000',
          isManualEdition: true,
          latitude: 43.609296,
          longitude: 3.882445,
          banId: '49759_1304_00002',
          departmentCode: '34',
          inseeCode: '34172',
          label: 'Centre commercial',
        },
      },
      isOfferAddressEnabled: true,
    })

    const expectedFormValues = {
      street: '79 Quai du Palladium',
      postalCode: '34000',
      city: 'Montpellier',
      addressAutocomplete: '79 Quai du Palladium 34000 Montpellier',
      'search-addressAutocomplete': '79 Quai du Palladium 34000 Montpellier',
      coords: '43.609296, 3.882445',
      latitude: '43.609296',
      longitude: '3.882445',
      banId: '49759_1304_00002',
      manuallySetAddress: true,
      comment: '',
      bookingEmail: '',
      name: 'Lieu de test',
      venueSiret: null,
      publicName: 'Adresse de la venue',
      siret: '',
      venueLabel: '',
      venueType: 'Centre culturel',
      withdrawalDetails: '',
      isWithdrawalAppliedOnAllOffers: false,
    }

    expect(formValues).toEqual(expectedFormValues)
  })
})
