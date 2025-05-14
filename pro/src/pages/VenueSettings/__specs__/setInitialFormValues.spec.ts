import { GetVenueResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'

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
    })

    const expectedFormValues = {
      street: '79 Quai du Palladium',
      postalCode: '34000',
      inseeCode: '34172',
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
      venueSiret: '',
      publicName: 'Adresse de la venue',
      siret: '',
      venueType: 'Centre culturel',
      withdrawalDetails: '',
    }

    expect(formValues).toEqual(expectedFormValues)
  })

  it('should return empty inseeCode and null banId if address is not provided', () => {
    const formValues = setInitialFormValues({
      venue: {
        ...venue,
        address: null,
      },
    })

    expect(formValues.inseeCode).toBeNull()
    expect(formValues.banId).toBeNull()
    // Check other address-related fields to ensure they are also handled correctly
    expect(formValues.street).toEqual('')
    expect(formValues.postalCode).toEqual('')
    expect(formValues.city).toEqual('')
    expect(formValues.addressAutocomplete).toEqual('undefined undefined') // Corresponds to `${autoCompleteStreet}${venue.address?.postalCode} ${venue.address?.city}`
    expect(formValues['search-addressAutocomplete']).toEqual(
      'undefined undefined'
    )
    expect(formValues.coords).toEqual('undefined, undefined')
    expect(formValues.latitude).toEqual('undefined')
    expect(formValues.longitude).toEqual('undefined')
    expect(formValues.manuallySetAddress).toBeUndefined()
  })

  it('should return empty inseeCode if inseeCode is missing in address', () => {
    const formValues = setInitialFormValues({
      venue: {
        ...venue,
        address: {
          ...venue.address!, // Ensure address is not null
          inseeCode: undefined,
        },
      },
    })
    expect(formValues.inseeCode).toBeNull()
  })

  it('should return null banId if banId is missing in address', () => {
    const formValues = setInitialFormValues({
      venue: {
        ...venue,
        address: {
          ...venue.address!, // Ensure address is not null
          banId: undefined,
        },
      },
    })
    expect(formValues.banId).toBeNull()
  })
})
