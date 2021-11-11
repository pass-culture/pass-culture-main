/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt rtl "Gaël: migration from enzyme to RTL"
*/

import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Link, Router } from 'react-router-dom'

import OffererItem from '../OffererItem'

describe('src | components | pages | Offerers | OffererItem | OffererItem', () => {
  let props
  let history

  const dispatchMock = jest.fn()
  const parseMock = () => ({ 'mots-cles': null })
  const queryChangeMock = jest.fn()

  beforeEach(() => {
    props = {
      currentUser: {},
      isVenueCreationAvailable: true,
      dispatch: dispatchMock,
      offerer: {
        id: 'AE',
        name: 'Fake Name',
        nOffers: 0,
        isValidated: true,
      },
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
      venues: [
        {
          isDigital: true,
        },
      ],
      physicalVenues: [{}],
    }
    history = createBrowserHistory()
  })

  describe('render', () => {
    describe('navigate to offerer caret', () => {
      it('should be displayed with right link', () => {
        // given
        // given
        props.offerer = {
          id: 'AE',
          isValidated: true,
          name: 'Validated Offerer',
          nOffers: 0,
          userHasAccess: true,
        }

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const caret = wrapper.find('.caret')
        const navLink = caret.find(Link)

        // then
        expect(navLink.prop('to')).toBe('/accueil?structure=AE')
      })
    })

    describe('offerer name', () => {
      it('should be rendered with a link', () => {
        // given
        props.venues = [
          {
            isVirtual: true,
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const createOffer = wrapper.find('.name')
        const navLink = createOffer.find(Link)

        // then
        expect(navLink.text()).toBe('Fake Name')
        expect(navLink.prop('to')).toBe('/accueil?structure=AE')
      })
    })

    describe('create an offer', () => {
      describe('when offerer has only one virtual venue', () => {
        it('should display a link to create digital offer', () => {
          // given
          props.venues = [
            {
              isVirtual: true,
              id: 'DY',
            },
          ]
          // when
          const wrapper = mount(
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre numérique')
          expect(navLink.prop('to')).toBe('/offres/creation?structure=AE&lieu=DY')
        })
      })

      describe('when offerer has one virtual venue and only one physical venue', () => {
        it('should display a link to create offer', () => {
          // given
          props.venues = [
            {
              isVirtual: true,
              id: 'DY',
            },
            {
              isVirtual: false,
              id: 'HD',
            },
          ]
          // when
          const wrapper = mount(
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre')
          expect(navLink.prop('to')).toBe('/offres/creation?structure=AE')
        })
      })
    })

    describe('display offers total number', () => {
      it('should display total and link to offers page', () => {
        // given
        props.offerer.nOffers = 42
        props.venues = [
          {
            isVirtual: true,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'HD',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )

        const offersCount = wrapper.findWhere(node => node.text() === '42 offres').first()

        // then
        expect(offersCount).toHaveLength(1)
        expect(offersCount.find('a').at(0).prop('href')).toBe('/offres?structure=AE')
      })

      it('should display 0 offer and no link to offers page when offerer has no offers', () => {
        // given
        props.offerer.nOffers = 0
        props.venues = [
          {
            isVirtual: true,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'HD',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )

        // then
        const offersCount = wrapper.find({ children: '0 offre' })
        const offersLink = offersCount.find('a')
        expect(offersCount).toHaveLength(1)
        expect(offersLink).toHaveLength(0)
      })
    })

    describe('display physical venues total number', () => {
      it('should display total with a link to offers page', () => {
        // given
        props.offerer.nOffers = 42
        props.physicalVenues = [
          {
            isVirtual: false,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'FL',
          },
          {
            isVirtual: false,
            id: 'DQ',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const actions = wrapper.find('#count-venues-action')
        const navLink = actions.find(Link)

        // then
        expect(navLink.text()).toBe('3 lieux')
        expect(navLink.at(0).prop('to')).toBe('/structures/AE/')
      })

      it('should display 0 venue with a link to offerer page', () => {
        // given
        props.offerer.nOffers = 0
        props.physicalVenues = []

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const actions = wrapper.find('#count-venues-action')
        const navLink = actions.find(Link)

        // then
        expect(navLink.text()).toBe('0 lieu')
        expect(navLink.at(0).prop('to')).toBe('/structures/AE/')
      })
    })

    describe('add new venue link', () => {
      it('should display a link to create a new venue', () => {
        // given
        props.offerer = {
          id: 'AE',
          name: 'Fake Name',
          nOffers: 0,
          isValidated: false,
        }

        // when
        const wrapper = shallow(<OffererItem {...props} />)
        const createVenueLink = wrapper.find('#create-venue-action').find(Link)

        // then
        expect(createVenueLink.prop('to')).toBe('/structures/AE/lieux/creation')
      })

      it('should redirect to unavailable page when venue creation is not available', () => {
        // given
        props.isVenueCreationAvailable = false
        props.offerer = {
          id: 'AE',
          name: 'Fake Name',
          nOffers: 0,
          isValidated: false,
        }

        // when
        const wrapper = shallow(<OffererItem {...props} />)
        const createVenueLink = wrapper.find('#create-venue-action').find(Link)

        // then
        expect(createVenueLink.prop('to')).toBe('/erreur/indisponible')
      })
    })
  })
})
