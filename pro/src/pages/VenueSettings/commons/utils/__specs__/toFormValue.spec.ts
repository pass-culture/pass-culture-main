import type { GetVenueResponseModel } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'

import { toFormValues } from '../toFormValues'

let venue: GetVenueResponseModel

describe('toFormValues', () => {
  beforeEach(() => {
    venue = {
      ...defaultGetVenue,
      publicName: 'Adresse de la venue',
    }
  })

  it('should return a valid initial form object', () => {
    const formValues = toFormValues({
      venue: {
        ...venue,
        location: {
          id: 978,
          //id: 1012,
          isVenueLocation: false,
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
    const formValues = toFormValues({
      venue: {
        ...venue,
        location: null,
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
    expect(formValues.manuallySetAddress).toBe(false)
  })

  it('should return empty inseeCode if inseeCode is missing in address', () => {
    const formValues = toFormValues({
      venue: {
        ...venue,
        location: {
          ...venue.location!, // Ensure address is not null
          inseeCode: undefined,
        },
      },
    })
    expect(formValues.inseeCode).toBeNull()
  })

  it('should return null banId if banId is missing in address', () => {
    const formValues = toFormValues({
      venue: {
        ...venue,
        location: {
          ...venue.location!, // Ensure address is not null
          banId: undefined,
        },
      },
    })
    expect(formValues.banId).toBeNull()
  })

  it('should return null banId if banId is missing in address', () => {
    const formValues = toFormValues({
      venue: {
        ...venue,
        isCaledonian: true,
        siret: 'NC0123456789XX',
        location: {
          ...venue.location!, // Ensure address is not null
          banId: undefined,
        },
      },
    })
    expect(formValues.siret).toEqual('0123456789')
  })
})
