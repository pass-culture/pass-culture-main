import React from 'react'
import { shallow } from 'enzyme'
import configureStore from 'redux-mock-store'

import RawOffer from '../RawOffer'
import MediationsManager from '../MediationsManager/index'
import { requestData } from 'redux-saga-data'

import { offerNormalizer } from 'utils/normalizers'

const dispatchMock = jest.fn()

// jest.mock('redux-saga-data', () => ({
// requestData: jest.fn(),
//}))

describe('src | components | pages | Offer | RawOffer ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        location: {
          search: '?lieu=AQ',
        },
        match: {
          params: {
            offerId: 'N9',
          },
        },
        currentUser: {
          isAdmin: false,
        },
        query: {
          parse: () => ({ lieu: 'AQ' }),
        },
        dispatch: dispatchMock,
        venues: [],
      }

      // when
      const wrapper = shallow(<RawOffer {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('MediationsManager', () => {
      it("should be displayed when it's not a new offer", () => {
        // given
        const initialProps = {
          location: {
            search: '?lieu=AQ',
          },
          match: {
            params: {
              offerId: 'N9',
            },
          },
          currentUser: {
            isAdmin: false,
          },
          query: {
            parse: () => ({ lieu: 'AQ' }),
          },
          dispatch: dispatchMock,
          offer: {
            bookingEmail: 'fake@email.com',
            dateCreated: '2019-03-29T15:38:23.806900Z',
            dateModifiedAtLastProvider: '2019-03-29T15:38:23.806874Z',
            eventId: null,
            id: 'N9',
            idAtProviders: null,
            isActive: true,
            lastProviderId: null,
            modelName: 'Offer',
            thingId: '94',
            venueId: 'AQ',
          },
        }

        // when
        const wrapper = shallow(<RawOffer {...initialProps} />)
        const mediationsManagerComponent = wrapper.find(MediationsManager)

        // then
        expect(mediationsManagerComponent).toHaveLength(1)
      })
    })
  })
  describe('functions', () => {
    describe('handleDataRequest', () => {
      describe('When OfferId is not nouveau and venue is given', () => {
        it('should first dispatch requestData when Main component is rendered', () => {
          // given
          const initialProps = {
            location: {
              search: '?lieu=AQ',
            },
            match: {
              params: {
                offerId: 'N9',
              },
            },
            currentUser: {
              isAdmin: false,
            },
            history: {
              action: 'POP',
              location: {
                pathname: '/offres/N9',
                search: '?lieu=AQ',
                hash: '',
                state: undefined,
                key: 'c5cg3o',
              },
            },
            query: {
              parse: () => ({ lieu: 'AQ' }),
            },
            dispatch: dispatchMock,
            offerers: [],
            venues: [],
            providers: [],
            types: [],
          }

          // when
          const wrapper = shallow(<RawOffer {...initialProps} />)

          const handleSuccess = jest.fn(() => {})
          // const handleSuccess = jest.fn(() => {data: {venues: []}})
          // FIXME

          console.log('GET STATE in test', wrapper.state())
          console.log('props in test', wrapper.props())

          wrapper.props().handleDataRequest(handleSuccess)
          const expectedRequestedGetTypes = {
            keepComponentMounted: undefined,
            type: 'CLOSE_MODAL',
          }

          const toto3 = {
            config: {
              apiPath: '/offers/N9',
              method: 'GET',
              normalizer: offerNormalizer,
              stateKey: 'offers',
            },
            type: 'REQUEST_DATA_GET_OFFERS',
          }

          const toto4 = {
            config: {
              apiPath: '/offerers',
              method: 'GET',
              normalizer: {
                managedVenues: 'venues',
              },
            },
            type: 'REQUEST_DATA_GET_/OFFERERS',
          }

          const toto5 = {
            config: {
              apiPath: '/providers',
              method: 'GET',
            },
            type: 'REQUEST_DATA_GET_/PROVIDERS',
          }

          const toto6 = {
            config: {
              apiPath: '/types',
              method: 'GET',
            },
            type: 'REQUEST_DATA_GET_/TYPES',
          }

          // then
          expect(dispatchMock).toHaveBeenCalled()
          expect(dispatchMock.mock.calls.length).toEqual(7)
          expect(dispatchMock.mock.calls[0][0]).toEqual(
            expectedRequestedGetTypes
          )
          expect(dispatchMock.mock.calls[1][0]).toEqual(
            expectedRequestedGetTypes
          )
          expect(dispatchMock.mock.calls[2][0]).toEqual(
            expectedRequestedGetTypes
          )
          expect(dispatchMock.mock.calls[3][0]).toEqual(toto3)
          expect(dispatchMock.mock.calls[4][0]).toEqual(toto4)
          expect(dispatchMock.mock.calls[5][0]).toEqual(toto5)
          expect(dispatchMock.mock.calls[6][0]).toEqual(toto6)
        })
      })
      describe.skip('When venueId', () => {
        it('????', () => {
          // query parse {lieu: "DY"}
          // RawOffer.js:118  QQQQQQQQQQQ       Venue Id  DY
          // RawOffer.js:119  QQQQQQQQQQQ       OffererID undefined
          // je créé un lieu et je peux ajouter une offre http://localhost:3001/offres/nouveau?lieu=DY
        })
      })
      describe.skip('When OfferId is nouveau', () => {
        // /offres/nouveau?structure=BU

        // venueId est undefined  // offererId = BU

        it('should  ', () => {
          // given
          const initialProps = {
            location: {
              search: '?structure=BU',
            },
          }

          // when

          // then
        })
      })
      describe('When no venue at all and new offer', () => {
        it('should display modal', () => {
          // query parse {}
          // RawOffer.js:118  QQQQQQQQQQQ       Venue Id  undefined
          // RawOffer.js:119  QQQQQQQQQQQ       OffererID undefined
        })
      })
      describe('When one venue and new offer', () => {
        it('???', () => {
          // url : http://localhost:3001/offres/nouveau
          // Venue Id  undefined
          // OffererID undefined

          // given

          const initialProps = {
            history: {},
            dispatch: dispatchMock,
            match: {
              params: { offerId: 'nouveau' },
            },
            offerers: [],
            venues: [],
            providers: [],
            query: {
              parse: () => ({}),
            },
            types: [],
          }
        })
      })
    })
  })
})
