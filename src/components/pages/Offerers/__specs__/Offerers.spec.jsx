import React from 'react'
import { shallow } from 'enzyme'

import Offerers from '../Offerers'

describe('src | components | pages | Offerers | Offerers', () => {
  let change
  let dispatch
  let parse
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    change = jest.fn()
    parse = () => ({ 'mots-cles': null })

    props = {
      currentUser: {},
      dispatch,
      offerers: [{ id: 'AE' }],
      pendingOfferers: [],
      pagination: {
        apiQuery: {
          keywords: null,
        },
      },
      query: {
        change,
        parse,
      },
      location: {
        search: '',
      },
    }
  })

  afterEach(() => {
    dispatch.mockClear()
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Offerers {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {

    describe('should pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }]
        props.pendingOfferers = []

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then

        expect(heroSection.title).toStrictEqual('Votre structure juridique')
      })

      it('should display Vos structures when many offerers', () => {
        // given
          props.currentUser = {}
          props.offerers = [{ id: 'AE' }, { id: 'AF' }]
          props.pendingOfferers = []

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toStrictEqual('Vos structures juridiques')
      })
    })

    describe('should display a notification', () => {
      it("should display a notification when current user has no offers and has digital venues", () => {
        // given
        props.currentUser = {
          hasOffers: false,
          hasPhysicalVenues: false,
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
        expect(dispatch.mock.calls[2]).toStrictEqual(expected)
      })

      it("should display a notification when current user has only digital offers", () => {
        // given
        props.currentUser = {
          hasOffers: true,
          hasPhysicalVenues: false,
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
        expect(dispatch.mock.calls[2]).toStrictEqual(expected)
      })
    })

    describe('should not display a notification', () => {
      it("should not display a notification when current user has offers and physical venues", () => {
        // given
        props.currentUser = {
          hasOffers: true,
          hasPhysicalVenues: true,
        }

        // when
        shallow(<Offerers {...props} />)

        // then
        const expected = [
          {
            "config": {
              "apiPath": "/offerers?keywords&validated=false",
              "method": "GET",
              "normalizer": {
                "managedVenues": {
                  "normalizer": {"offers": "offers"},
                  "stateKey": "venues"}
                },
                "stateKey": "pendingOfferers"},
                "type": "REQUEST_DATA_GET_PENDINGOFFERERS"
          }
        ]
        expect(dispatch.mock.calls[2]).toStrictEqual(expected)
      })

      it("should not display a notification when current user has no offers but physical venues", () => {
        // given
        props.currentUser = {
          hasOffers: false,
          hasPhysicalVenues: true,
        }

        // when
        shallow(<Offerers {...props} />)

        // then
        const expected = [
          {
            "config": {
              "apiPath": "/offerers?keywords&validated=false",
              "method": "GET",
              "normalizer": {
                "managedVenues": {
                  "normalizer": {"offers": "offers"},
                  "stateKey": "venues"}
                },
                "stateKey": "pendingOfferers"},
                "type": "REQUEST_DATA_GET_PENDINGOFFERERS"
          }
        ]
        expect(dispatch.mock.calls[2]).toStrictEqual(expected)
      })
    })

  })
})
