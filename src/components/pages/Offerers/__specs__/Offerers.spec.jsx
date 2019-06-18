import React from 'react'
import { shallow } from 'enzyme'

import Offerers from '../Offerers'

const dispatchMock = jest.fn()
const parseMock = () => ({ 'mots-cles': null })
const queryChangeMock = jest.fn()

describe('src | components | pages | Offerers | Offerers', () => {
  afterEach(
    dispatchMock.mockClear()
  )
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: dispatchMock,
        offerers: [{ id: 'AE' }],
        pendingOfferers: [],
        pagination: {
          apiQuery: {
            keywords: null,
          },
        },
        query: {
          change: queryChangeMock,
          parse: parseMock,
        },
        location: {
          search: '',
        },
      }

      // when
      const wrapper = shallow(<Offerers {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          offerers: [{ id: 'AE' }],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
          query: {
            change: queryChangeMock,
            parse: parseMock,
          },
          location: {
            search: '',
          },
        }

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then

        expect(heroSection.title).toEqual('Votre structure juridique')
      })
      it('should display Vos structures when many offerers', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          offerers: [{ id: 'AE' }, { id: 'AF' }],
          pendingOfferers: [],
          pagination: {
            apiQuery: {
              keywords: null,
            },
          },
          query: {
            change: queryChangeMock,
            parse: parseMock,
          },
          location: {
            search: '',
          },
        }

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toEqual('Vos structures juridiques')
      })
    })
    describe('display a notification', () => {
      it("should display a notification when current user's has one virtual offer so no physical venues yet", () => {
        // given
        const props = {
          currentUser: {
            hasOffers: true,
            hasPhysicalVenues: true,
            isAdmin: true,
          },
          dispatch: dispatchMock,
          location: {
            search: '',
          },
          offerers : [],
          pendingOfferers: [],
          query: {
            parse: parseMock,
          },
        }

        // when
        shallow(<Offerers {...props} />)

        // then
        const expected = [
          {
          	"patch": {
          		"tag": "offerers",
          		"text": "Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)",
          		"type": "info",
          		"url": "/structures/AE/lieux/creation",
          		"urlLabel": "Nouveau lieu"
          	},
          	"type": "SHOW_NOTIFICATION"
          }
        ]
        expect(dispatchMock.mock.calls[2]).toEqual(expected)
      })
    })
  })
})
