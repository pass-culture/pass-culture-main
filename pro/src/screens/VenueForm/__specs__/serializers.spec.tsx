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
  bookingEmail: 'em@ail.fr',
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
  reimbursementPointId: 91,
}

describe('screen | VenueForm | serializers', () => {
  it('Serialize form value for venue creation with siret', async () => {
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: false,
      offererId: 'EA',
    })

    expect(result.siret).toBeDefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue creation with venueLabelId', async () => {
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: true,
      offererId: 'EA',
    })

    expect(result.venueLabelId).not.toBeNull()
  })

  it('Serialize form value for venue updating with comment', async () => {
    const result = serializeEditVenueBodyModel(formValues, {
      hideSiret: true,
    })

    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })

  it('Serialize form value for venue updating with venueLabelId', async () => {
    const result = serializeEditVenueBodyModel(formValues, {
      hideSiret: true,
    })

    expect(result.venueLabelId).not.toBeNull()
  })

  it('Serialize form value for venue creation without venueLabelId', async () => {
    const formValues: IVenueFormValues = {
      bannerMeta: undefined,
      comment: 'Commentaire',
      description: '',
      isVenueVirtual: false,
      bookingEmail: 'em@ail.fr',
      name: 'MINISTERE DE LA CULTURE',
      publicName: 'Melodie Sims',
      siret: '881 457 238 23022',
      venueType: 'GAMES',
      venueLabel: '',
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
      reimbursementPointId: 91,
    }
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: true,
      offererId: 'EA',
    })

    expect(result.venueLabelId).toBeNull()
  })

  it('Serialize form value for venue updating with siret', async () => {
    const result = serializeEditVenueBodyModel(formValues, { hideSiret: false })

    expect(result.siret).not.toBeUndefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue updating with comment', async () => {
    const result = serializeEditVenueBodyModel(formValues, { hideSiret: true })

    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })
})
