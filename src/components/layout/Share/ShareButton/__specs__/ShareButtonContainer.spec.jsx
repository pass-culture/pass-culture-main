import { selectCurrentUser } from 'with-react-redux-login'

import { mapStateToProps } from '../ShareButtonContainer'
import { getShareURL } from '../../../../../helpers'
import { mapDispatchToProps, mergeProps } from '../ShareButtonContainer'

jest.mock('with-react-redux-login')
jest.mock('../../../../../helpers')

describe('src | components | share | ShareButtonContainer', () => {
  describe('mapStateToProps', () => {
    describe('when mapping offerName', () => {
      it('should get offerName from current offer', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId,
            },
          },
        }
        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation],
          },
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.offerName).toBe(offer.name)
      })
    })

    describe('when mapping text', () => {
      it('should build text from offerName', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId,
            },
          },
        }
        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation],
          },
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.text).toBe('Retrouvez Marx et Compagnie sur le pass Culture')
      })
    })

    describe('when mapping url', () => {
      describe('when user is logged in', () => {
        it('should getShareURL with location and user', () => {
          // given
          const offerId = 'B4'
          const offer = {
            id: offerId,
            name: 'Marx et Compagnie',
          }
          const recommendation = {
            id: 'PA',
            mediationId: 'CA',
            offerId,
          }
          const ownProps = {
            match: {
              params: {
                mediationId: 'CA',
                offerId,
              },
            },
          }
          const state = {
            data: {
              bookings: [],
              favorites: [],
              mediations: [],
              offers: [offer],
              recommendations: [recommendation],
            },
          }

          // when
          selectCurrentUser.mockReturnValue({ id: 'myId' })
          getShareURL.mockReturnValue('http://fake_shared_url')

          // then
          expect(mapStateToProps(state, ownProps).url).toBe('http://fake_shared_url')
        })
      })
    })

    describe('when mapping offerId', () => {
      it('should get offerId from current offer', () => {
        // given
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }
        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [
              {
                id: 'B4',
                name: 'Marx et Compagnie',
              },
            ],
            recommendations: [
              {
                id: 'PA',
                mediationId: 'CA',
                offerId: 'B4',
              },
            ],
          },
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.offerId).toBe('B4')
      })
    })

    describe('when mapping share data', () => {
      it('should explode all attributes from share', () => {
        // given
        const offerId = 'B4'
        const offer = {
          id: offerId,
          name: 'Marx et Compagnie',
        }
        const recommendation = {
          id: 'PA',
          mediationId: 'CA',
          offerId,
        }
        const ownProps = {
          match: {
            params: {
              mediationId: 'CA',
              offerId: 'B4',
            },
          },
        }

        const state = {
          data: {
            bookings: [],
            favorites: [],
            mediations: [],
            offers: [offer],
            recommendations: [recommendation],
          },
          share: {
            options: null,
            visible: true,
          },
        }

        // when
        selectCurrentUser.mockReturnValue({ id: 'myId' })
        const result = mapStateToProps(state, ownProps)

        // then
        expect(result.options).toBeNull()
        expect(result.visible).toBe(true)
      })
    })
  })

  describe('mapDispatchToProps', () => {
    describe('when mapping openPopin', () => {
      it('should dispatch openSharePopin with correct arguments', () => {
        // given
        const dispatch = jest.fn()

        // when
        mapDispatchToProps(dispatch).openPopin({ isOpened: true })

        // then
        expect(dispatch).toHaveBeenCalledWith({
          options: { isOpened: true },
          type: 'TOGGLE_SHARE_POPIN',
        })
      })
    })

    describe('when mapping closePopin', () => {
      it('should dispatch closeSharePopin with correct arguments', () => {
        // given
        const dispatch = jest.fn()

        // when
        mapDispatchToProps(dispatch).closePopin()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          options: null,
          type: 'TOGGLE_SHARE_POPIN',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should spread stateProps and dispatch props into mergedProps', () => {
      // given
      const stateProps = {
        offerId: 'B4',
      }
      const dispatchProps = {
        openPopin: () => {},
        closePopin: () => {},
      }

      // when
      const mergedProps = mergeProps(stateProps, dispatchProps)

      // then
      expect(mergedProps).toStrictEqual({
        offerId: 'B4',
        openPopin: expect.any(Function),
        closePopin: expect.any(Function),
        trackShareOfferByMail: expect.any(Function),
        trackShareOfferByLink: expect.any(Function),
      })
    })

    it('should map a tracking event for sharing an offer by mail', () => {
      // given
      const stateProps = {
        offerId: 'B4',
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackShareOfferByMail()

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({ action: 'shareMail', name: 'B4' })
    })

    it('should map a tracking event for sharing an offer by link', () => {
      // given
      const stateProps = {
        offerId: 'B4',
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      // when
      mergeProps(stateProps, {}, ownProps).trackShareOfferByLink()

      // then
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({ action: 'shareLink', name: 'B4' })
    })
  })
})
