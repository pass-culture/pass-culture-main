import { getRedirectToOffersOrOfferers, getRedirectToSignin } from '../helpers'

describe('src | components | hocs | with-login | helpers', () => {
  describe('getRedirectToOffersOrOfferers', () => {
    describe('when the user is signin for the first time and has no offer and only a virtual venue created by default', () => {
      it('should redirect to offerers page', () => {
        // given
        const currentUser = {
          hasOffers: false,
          hasPhysicalVenues: false,
        }

        // when
        const result = getRedirectToOffersOrOfferers({ ...currentUser })

        // then
        expect(result).toStrictEqual('/structures')
      })
    })

    describe('when the user has a digital offer and only a virtual venue', () => {
      it('should redirect to offerers page', () => {
        // given
        const currentUser = {
          hasOffers: true,
          hasPhysicalVenues: false,
        }

        // when
        const result = getRedirectToOffersOrOfferers({ ...currentUser })

        // then
        expect(result).toStrictEqual('/structures')
      })
    })

    describe('when the user has no offers but a physical venue', () => {
      it('should redirect to offers page', () => {
        // given
        const currentUser = {
          hasOffers: false,
          hasPhysicalVenues: true,
        }

        // when
        const result = getRedirectToOffersOrOfferers({ ...currentUser })

        // then
        expect(result).toStrictEqual('/offres')
      })
    })

    describe('when the user has offers in physical venues', () => {
      it('should redirect to offers page', () => {
        // given
        const currentUser = {
          hasOffers: true,
          hasPhysicalVenues: true,
        }

        // when
        const result = getRedirectToOffersOrOfferers({ ...currentUser })

        // then
        expect(result).toStrictEqual('/offres')
      })
    })
  })

  describe('getRedirectToSignin', () => {
    describe('when the user is signin for the first time and has no offer and only a virtual venue created by default', () => {
      it('should redirect to offerers page', () => {
        // given
        const pathname = 'foo'
        const search = '?bar'

        // when
        const result = getRedirectToSignin({ pathname, search })

        // then
        expect(result).toStrictEqual('/connexion?de=foo%3Fbar')
      })
    })
  })
})
