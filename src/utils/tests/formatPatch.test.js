import {
  formatPatch,
  VENUE_EDIT_PATCH_KEYS,
  VENUE_NEW_PATCH_KEYS,
} from '../formatPatch'

describe('formatPatch', () => {
  describe('when creating new form', () => {
    it('should format the patch with permitted key', () => {
      // given
      const patch = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673@email.com',
        city: 'Aulnay-sous-Bois',
        comment: null,
        dateModifiedAtLastProvider: '2019-02-05T09:37:37.776590Z',
        departementCode: '93',
        firstThumbDominantColor: null,
        iban: 'FR7630001007941234567890185',
        id: 'ARRA',
        idAtProviders: null,
        isValidated: true,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        modelName: 'Venue',
        name: 'Cinéma de la fin',
        postalCode: '93600',
        siret: '22222222911111',
        thumbCount: 0,
        venueProvidersIds: [],
      }
      const config = { isNew: true, isEdit: false }

      // when
      const result = formatPatch(
        patch,
        config,
        VENUE_NEW_PATCH_KEYS,
        VENUE_EDIT_PATCH_KEYS
      )
      const expected = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673@email.com',
        city: 'Aulnay-sous-Bois',
        iban: 'FR7630001007941234567890185',
        latitude: 48.92071,
        longitude: 2.48371,
        name: 'Cinéma de la fin',
        postalCode: '93600',
        siret: '22222222911111',
      }
      // then
      expect(result).toEqual(expected)
    })
  })

  describe('when editing form', () => {
    it('should format the patch with permitted key', () => {
      // given
      const patch = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673@email.com',
        city: 'Aulnay-sous-Bois',
        comment: null,
        dateModifiedAtLastProvider: '2019-02-05T09:37:37.776590Z',
        departementCode: '93',
        firstThumbDominantColor: null,
        iban: 'FR7630001007941234567890185',
        id: 'ARRA',
        idAtProviders: null,
        isValidated: true,
        isVirtual: false,
        lastProviderId: null,
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        modelName: 'Venue',
        name: 'Cinéma de la fin',
        postalCode: '93600',
        siret: '22222222911111',
        thumbCount: 0,
        venueProvidersIds: [],
      }
      const config = { isEdit: true }

      // when
      const result = formatPatch(
        patch,
        config,
        VENUE_NEW_PATCH_KEYS,
        VENUE_EDIT_PATCH_KEYS
      )

      // then
      expect(result).toEqual({
        bookingEmail: 'R6465373fake674654673@email.com',
      })
    })
  })
})
