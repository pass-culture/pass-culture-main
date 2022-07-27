import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Link, Router } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import OffererItem from '../OffererItem'

describe('src | components | pages | Offerers | OffererItem | OffererItem', () => {
  let props
  let history
  let store

  const dispatchMock = jest.fn()
  const parseMock = () => ({ 'mots-cles': null })
  const queryChangeMock = jest.fn()

  beforeEach(() => {
    store = configureTestStore({})
    props = {
      currentUser: {},
      isVenueCreationAvailable: true,
      dispatch: dispatchMock,
      offerer: {
        id: 'AE',
        name: 'Fake Name',
        nOffers: 0,
        isValidated: true,
        managedVenues: [
          {
            id: 'NV',
            isVirtual: false,
          },
          {
            id: 'VV',
            isVirtual: true,
          },
        ],
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
    }
    history = createBrowserHistory()
  })

  describe('render', () => {
    describe('navigate to offerer caret', () => {
      it('should be displayed with right link', () => {
        // given
        props.offerer = {
          id: 'AE',
          isValidated: true,
          name: 'Validated Offerer',
          nOffers: 0,
          userHasAccess: true,
          managedVenues: [
            {
              id: 'NV',
              isVirtual: false,
            },
            {
              id: 'VV',
              isVirtual: true,
            },
          ],
        }

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const caret = wrapper.find('.caret')
        const navLink = caret.find(Link)

        // then
        expect(navLink.prop('to')).toBe('/accueil?structure=AE')
      })
    })

    describe('offerer name', () => {
      it('should be rendered with a link', () => {
        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
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
          props.offerer.managedVenues = [
            {
              isVirtual: true,
              id: 'DY',
            },
          ]
          // when
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <OffererItem {...props} />
              </Router>
            </Provider>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre numérique')
          expect(navLink.prop('to')).toBe(
            '/offre/creation?structure=AE&lieu=DY'
          )
        })
      })

      describe('when offerer has one virtual venue and only one physical venue', () => {
        it('should display a link to create offer', () => {
          // when
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <OffererItem {...props} />
              </Router>
            </Provider>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre')
          expect(navLink.prop('to')).toBe('/offre/creation?structure=AE')
        })
      })
    })

    describe('display offers total number', () => {
      it('should display total and link to offers page', () => {
        // given
        props.offerer.nOffers = 42

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )

        const offersCount = wrapper
          .findWhere(node => node.text() === '42 offres')
          .first()

        // then
        expect(offersCount).toHaveLength(1)
        expect(offersCount.find('a').at(0).prop('href')).toBe(
          '/offres?structure=AE'
        )
      })

      it('should display 0 offer and no link to offers page when offerer has no offers', () => {
        // given
        props.offerer.nOffers = 0

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
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
        props.offerer.managedVenues = [
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
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
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
        props.offerer.managedVenues = []

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
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
          managedVenues: [],
        }

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
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
          managedVenues: [],
        }

        // when
        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const createVenueLink = wrapper.find('#create-venue-action').find(Link)

        // then
        expect(createVenueLink.prop('to')).toBe('/erreur/indisponible')
      })
    })
  })
})
