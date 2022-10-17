import '@testing-library/jest-dom'

import { IVenueFormValues } from 'new_components/VenueForm'

import {
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from '../serializers'

const formValues: IVenueFormValues = {
  bannerMeta: undefined,
  comment: 'Commentaire',
  description: '',
  isVenueVirtual: false,
  mail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '881 457 238 23022',
  venueType: 'GAMES',
  venueLabel: 'BM',
  departmentCode: '',
  address: 'PARIS',
  additionalAddress: '',
  addressAutocomplete: 'Allee Rene Omnes 35400 Saint-Malo',
  'search-addressAutocomplete': 'PARIS',
  city: 'Saint-Malo',
  latitude: 48.635699,
  longitude: -2.006961,
  postalCode: '35400',
  accessibility: {
    visual: false,
    mental: true,
    audio: false,
    motor: true,
    none: false,
  },
  isAccessibilityAppliedOnAllOffers: false,
  phoneNumber: '0604855967',
  email: 'em@ail.com',
  webSite: 'https://www.site.web',
  isPermanent: false,
  id: '',
  bannerUrl: '',
  withdrawalDetails: 'Oui',
  isWithdrawalAppliedOnAllOffers: false,
}

describe('screen | VenueForm | serializers', () => {
  it('Serialize form value for venue creation with siret', async () => {
    // Given
    const result = serializePostVenueBodyModel(formValues, true, 'EA')

    // Then
    expect(result.siret).toBeDefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue creation with comment', async () => {
    // Given
    const result = serializePostVenueBodyModel(formValues, false, 'EA')

    // Then
    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })

  it('Serialize form value for venue updating with siret', async () => {
    const result = serializeEditVenueBodyModel(formValues, [], true)

    // Then
    expect(result.siret).not.toBeUndefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue updating with comment', async () => {
    const result = serializeEditVenueBodyModel(formValues, [], false)

    // Then
    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })
})
