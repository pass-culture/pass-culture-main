import { EditVenueBodyModel } from 'apiClient/v1'
import { VenueFormValues } from 'components/VenueCreationForm'

import {
  EditVirtualVenueBodyModel,
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from '../../../pages/VenueEdition/serializers'

const formValues: VenueFormValues = {
  bannerMeta: undefined,
  comment: 'Commentaire',
  description: '',
  isVenueVirtual: false,
  bookingEmail: 'em@ail.fr',
  name: 'MINISTERE DE LA CULTURE',
  publicName: 'Melodie Sims',
  siret: '881 457 238 23022',
  venueType: 'GAMES',
  venueLabel: '5',
  departmentCode: '',
  address: 'PARIS',
  banId: '35288_7283_00001',
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
  id: undefined,
  bannerUrl: '',
  withdrawalDetails: 'Oui',
  venueSiret: null,
  isWithdrawalAppliedOnAllOffers: false,
  reimbursementPointId: 91,
}

describe('screen | VenueForm | serializers', () => {
  it('Serialize form value for venue creation with siret', () => {
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: false,
      offererId: 12,
    })

    expect(result.siret).toBeDefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue creation with venueLabelId', () => {
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: true,
      offererId: 13,
    })

    expect(result.venueLabelId).not.toBeNull()
  })

  it('Serialize form value for venue updating with comment', () => {
    const result: EditVenueBodyModel = serializeEditVenueBodyModel(formValues, {
      hideSiret: true,
    })

    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })

  it('Serialize form value for venue updating with venueLabelId', () => {
    const result: EditVenueBodyModel = serializeEditVenueBodyModel(formValues, {
      hideSiret: true,
    })

    expect(result.venueLabelId).not.toBeNull()
  })

  it('Serialize form value for venue creation without venueLabelId', () => {
    const formValues: VenueFormValues = {
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
      banId: '35288_7283_00001',
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
      id: undefined,
      bannerUrl: '',
      withdrawalDetails: 'Oui',
      venueSiret: null,
      isWithdrawalAppliedOnAllOffers: false,
      reimbursementPointId: 91,
    }
    const result = serializePostVenueBodyModel(formValues, {
      hideSiret: true,
      offererId: 13,
    })

    expect(result.venueLabelId).toBeNull()
  })

  it('Serialize form value for venue updating with siret', () => {
    const result: EditVenueBodyModel = serializeEditVenueBodyModel(formValues, {
      hideSiret: false,
    })

    expect(result.siret).not.toBeUndefined()
    expect(result.comment).toEqual('')
  })

  it('Serialize form value for venue updating with comment', () => {
    const result: EditVenueBodyModel = serializeEditVenueBodyModel(formValues, {
      hideSiret: true,
    })

    expect(result.siret).toBeUndefined()
    expect(result.comment).not.toEqual('')
  })

  describe('optional fields', () => {
    it('User should be able to create a venue without contact info', () => {
      const result = serializePostVenueBodyModel(
        {
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
          banId: '35288_7283_00001',
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
          phoneNumber: null,
          email: null,
          webSite: null,
          isPermanent: false,
          id: undefined,
          bannerUrl: '',
          withdrawalDetails: 'Oui',
          venueSiret: null,
          isWithdrawalAppliedOnAllOffers: false,
          reimbursementPointId: 91,
        },
        {
          hideSiret: false,
          offererId: 12,
        }
      )

      expect(result.contact?.email).toBeNull()
      expect(result.contact?.website).toBeNull()
      expect(result.contact?.phoneNumber).toBeNull()
    })

    it("User should be able to delete a venue's contact info", () => {
      const result: EditVenueBodyModel = serializeEditVenueBodyModel(
        {
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
          banId: '35288_7283_00001',
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
          phoneNumber: '',
          email: '',
          webSite: '',
          isPermanent: false,
          id: undefined,
          bannerUrl: '',
          withdrawalDetails: 'Oui',
          venueSiret: null,
          isWithdrawalAppliedOnAllOffers: false,
          reimbursementPointId: 91,
        },
        {
          hideSiret: false,
        }
      )

      expect(result.contact?.email).toBeNull()
      expect(result.contact?.website).toBeNull()
      expect(result.contact?.phoneNumber).toBeNull()
    })

    it('User should be able to create a venue without a venueLabel', () => {
      const result = serializePostVenueBodyModel(
        {
          bannerMeta: undefined,
          comment: 'Commentaire',
          description: '',
          isVenueVirtual: false,
          bookingEmail: 'em@ail.fr',
          name: 'MINISTERE DE LA CULTURE',
          publicName: 'Melodie Sims',
          siret: '881 457 238 23022',
          venueType: 'GAMES',
          venueLabel: null,
          departmentCode: '',
          address: 'PARIS',
          banId: '35288_7283_00001',
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
          phoneNumber: null,
          email: null,
          webSite: null,
          isPermanent: false,
          id: undefined,
          bannerUrl: '',
          withdrawalDetails: 'Oui',
          venueSiret: null,
          isWithdrawalAppliedOnAllOffers: false,
          reimbursementPointId: 91,
        },
        {
          hideSiret: false,
          offererId: 12,
        }
      )

      expect(result.venueLabelId).toBeNull()
    })

    it("User should be able to delete a venue's venueLabel", () => {
      const result: EditVenueBodyModel = serializeEditVenueBodyModel(
        {
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
          banId: '35288_7283_00001',
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
          phoneNumber: '',
          email: '',
          webSite: '',
          isPermanent: false,
          id: undefined,
          bannerUrl: '',
          withdrawalDetails: 'Oui',
          venueSiret: null,
          isWithdrawalAppliedOnAllOffers: false,
          reimbursementPointId: 91,
        },
        {
          hideSiret: false,
        }
      )

      expect(result.venueLabelId).toBeNull()
    })

    it('should only be able to update reimbursement point if virtual', () => {
      const result: EditVirtualVenueBodyModel = serializeEditVenueBodyModel(
        {
          bannerMeta: undefined,
          comment: 'Commentaire',
          description: '',
          isVenueVirtual: true,
          bookingEmail: 'em@ail.fr',
          name: 'MINISTERE DE LA CULTURE',
          publicName: 'Melodie Sims',
          siret: '881 457 238 23022',
          venueType: 'GAMES',
          venueLabel: '',
          departmentCode: '',
          address: 'PARIS',
          banId: '35288_7283_00001',
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
          phoneNumber: '',
          email: '',
          webSite: '',
          isPermanent: false,
          id: undefined,
          bannerUrl: '',
          withdrawalDetails: 'Oui',
          venueSiret: null,
          isWithdrawalAppliedOnAllOffers: false,
          reimbursementPointId: 91,
        },
        {
          hideSiret: false,
        }
      )

      expect(Object.keys(result).length).toEqual(1)
      expect(result.reimbursementPointId).not.toBeNull()
    })

    it('should be able to update virtual venue without a reimbursement', () => {
      const result: EditVirtualVenueBodyModel = serializeEditVenueBodyModel(
        {
          isVenueVirtual: true,
        } as VenueFormValues,
        {
          hideSiret: false,
        }
      )

      expect(Object.keys(result).length).toEqual(1)
      expect(result.reimbursementPointId).toBeNull()
    })
  })
})
