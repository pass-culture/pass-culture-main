import { formatVenuePayload } from '../formatVenuePayload'

describe('formatPatch', () => {
  describe('when creating new form', () => {
    it('should format the patch with permitted key', () => {
      // given
      const patch = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673sub@example.com',
        city: 'Aulnay-sous-Bois',
        comment: '',
        dateModifiedAtLastProvider: '2019-02-05T09:37:37.776590Z',
        departementCode: '93',
        iban: 'FR7630001007941234567890185',
        id: 'ARRA',
        isValidated: true,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        modelName: 'Venue',
        name: 'Cinéma de la fin',
        publicName: 'Cinéma de la fin des fins',
        postalCode: '93600',
        siret: '22222222911111',
      }

      // when
      const result = formatVenuePayload(patch, true)
      const expected = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673sub@example.com',
        city: 'Aulnay-sous-Bois',
        comment: '',
        description: '',
        iban: 'FR7630001007941234567890185',
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        name: 'Cinéma de la fin',
        publicName: 'Cinéma de la fin des fins',
        postalCode: '93600',
        siret: '22222222911111',
        venueTypeCode: null,
        venueLabelId: null,
      }
      // then
      expect(result).toStrictEqual(expected)
    })
  })

  describe('when editing form', () => {
    it('should format the patch with permitted key', () => {
      // given
      const patch = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673sub@example.com',
        city: 'Aulnay-sous-Bois',
        comment: 'comment',
        description: 'description',
        dateModifiedAtLastProvider: '2019-02-05T09:37:37.776590Z',
        departementCode: '93',
        iban: 'FR7630001007941234567890185',
        id: 'ARRA',
        isValidated: true,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        modelName: 'Venue',
        name: 'Cinéma de la fin',
        publicName: 'Cinéma de la fin publique',
        postalCode: '93600',
        siret: '22222222911111',
      }

      // when
      const result = formatVenuePayload(patch, false)

      // then
      expect(result).toStrictEqual({
        address: 'RUE DIDEROT',
        bookingEmail: 'R6465373fake674654673sub@example.com',
        comment: 'comment',
        description: 'description',
        city: 'Aulnay-sous-Bois',
        latitude: 48.92071,
        longitude: 2.48371,
        name: 'Cinéma de la fin',
        publicName: 'Cinéma de la fin publique',
        postalCode: '93600',
        siret: '22222222911111',
        venueTypeCode: null,
        venueLabelId: null,
      })
    })

    it('should preserve venueTypeCode and venueLabelId when empty', () => {
      // given
      const patch = {
        venueTypeCode: '',
        venueLabelId: '',
      }

      // when
      const result = formatVenuePayload(patch, false)

      // then
      expect(result).toStrictEqual({
        comment: '',
        venueTypeCode: '',
        venueLabelId: '',
        description: '',
      })
    })

    it('should format phoneNumber whend provided ', () => {
      // given
      const patch = {
        contact: {
          phoneNumber: '06.08-08(08.08',
        },
      }

      // when
      const result = formatVenuePayload(patch, false)

      // then
      expect(result).toStrictEqual({
        comment: '',
        contact: {
          phoneNumber: '+33608080808',
        },
        venueTypeCode: null,
        venueLabelId: null,
        description: '',
      })
    })
  })
})
