import React from 'react'
import { shallow } from 'enzyme'
import { withRedirectToOffersWhenAlreadyAuthenticated, redirectToUrl} from '../withRedirectToOffersWhenAlreadyAuthenticated'

const Test = () => null
const RedirectToOffersWhenAlreadyAuthenticatedTest = withRedirectToOffersWhenAlreadyAuthenticated(
  Test
)

describe('src | components | pages | hocs | with-login | withRedirectToOffersWhenAlreadyAuthenticated', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RedirectToOffersWhenAlreadyAuthenticatedTest />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('redirectToUrl', () => {
    describe('when the user is signin for the first time and has no offer and only a virtual venue created by default', () => {
      it('should redirect to offerers page', () => {
        // given
        const data = {currentUser: {
          hasOffers: false,
          hasPhysicalVenues: false
        }
      }

        // when
        const result = redirectToUrl(data)

        // then
        expect(result).toStrictEqual("/structures")
      })
    })

    describe('when the user has a digital offer and only a virtual venue', () => {
      it('should redirect to offerers page', () => {
        // given
        const data =  { currentUser: {
          hasOffers: true,
          hasPhysicalVenues: false
          }
        }

        // when
        const result = redirectToUrl(data)

        // then
        expect(result).toStrictEqual("/structures")
      })
    })

    describe('when the user has no offers but a physical venue', () => {
      it('should redirect to offers page', () => {
        // given
        const data = { currentUser: {
            hasOffers: false,
              hasPhysicalVenues: true
          }
        }

        // when
        const result = redirectToUrl(data)

        // then
        expect(result).toStrictEqual("/offres")
      })
    })

    describe('when the user has offers in physical venues', () => {
      it('should redirect to offers page', () => {
        // given
        const data = { currentUser: {
          hasOffers: true,
          hasPhysicalVenues: true
          }
        }

        // when
        const result = redirectToUrl(data)

        // then
        expect(result).toStrictEqual("/offres")
      })
    })
  })
})
