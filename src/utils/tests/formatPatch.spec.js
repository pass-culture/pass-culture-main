import { formatPatch } from '../formatPatch'

import {
  VENUE_MODIFICATION_PATCH_KEYS,
  VENUE_CREATION_PATCH_KEYS,
} from '../../components/pages/Venue/utils/utils'

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
        publicName: 'Cinéma de la fin des fins',
        postalCode: '93600',
        siret: '22222222911111',
        thumbCount: 0,
        venueProvidersIds: [],
      }
      const config = { isCreatedEntity: true, isModifiedEntity: false }

      // when
      const result = formatPatch(
        patch,
        config,
        VENUE_CREATION_PATCH_KEYS,
        VENUE_MODIFICATION_PATCH_KEYS
      )
      const expected = {
        address: 'RUE DIDEROT',
        bic: 'QSDFGH8Z564',
        bookingEmail: 'R6465373fake674654673@email.com',
        city: 'Aulnay-sous-Bois',
        iban: 'FR7630001007941234567890185',
        latitude: 48.92071,
        longitude: 2.48371,
        managingOffererId: 'APWA',
        name: 'Cinéma de la fin',
        publicName: 'Cinéma de la fin des fins',
        postalCode: '93600',
        siret: '22222222911111',
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
        bookingEmail: 'R6465373fake674654673@email.com',
        city: 'Aulnay-sous-Bois',
        comment: null,
        dateModifiedAtLastProvider: '2019-02-05T09:37:37.776590Z',
        departementCode: '93',
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
        publicName: 'Cinéma de la fin publique',
        postalCode: '93600',
        siret: '22222222911111',
        thumbCount: 0,
        venueProvidersIds: [],
      }
      const config = { isModifiedEntity: true }

      // when
      const result = formatPatch(
        patch,
        config,
        VENUE_CREATION_PATCH_KEYS,
        VENUE_MODIFICATION_PATCH_KEYS
      )

      // then
      expect(result).toStrictEqual({
        bookingEmail: 'R6465373fake674654673@email.com',
        publicName: 'Cinéma de la fin publique',

        address: 'RUE DIDEROT',
        city: 'Aulnay-sous-Bois',
        latitude: 48.92071,
        longitude: 2.48371,
        name: 'Cinéma de la fin',
        postalCode: '93600',
        siret: '22222222911111',
      })
    })
  })
})
