import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

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
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[0]
        // then
        expect(navLink).toHaveAttribute('href', '/accueil?structure=AE')
      })
    })

    describe('offerer name', () => {
      it('should be rendered with a link', () => {
        // when
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[0]

        // then
        expect(navLink).toHaveAttribute('href', '/accueil?structure=AE')
        expect(navLink).toHaveTextContent('Fake Name')
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
          render(
            <Provider store={store}>
              <Router history={history}>
                <OffererItem {...props} />
              </Router>
            </Provider>
          )

          const navLink = screen.getAllByRole('link')[1]

          // then
          expect(navLink).toHaveTextContent('Nouvelle offre numérique')
          expect(navLink).toHaveAttribute(
            'href',
            '/offre/creation?structure=AE&lieu=DY'
          )
        })
      })

      describe('when offerer has one virtual venue and only one physical venue', () => {
        it('should display a link to create offer', () => {
          // when
          render(
            <Provider store={store}>
              <Router history={history}>
                <OffererItem {...props} />
              </Router>
            </Provider>
          )
          const navLink = screen.getAllByRole('link')[1]

          // then
          expect(navLink).toHaveTextContent('Nouvelle offre')
          expect(navLink).toHaveAttribute(
            'href',
            '/offre/creation?structure=AE'
          )
        })
      })
    })

    describe('display offers total number', () => {
      it('should display total and link to offers page', () => {
        // given
        props.offerer.nOffers = 42

        // when
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getByText('42 offres')

        // then
        expect(navLink).toHaveAttribute('href', '/offres?structure=AE')
      })

      it('should display 0 offer and no link to offers page when offerer has no offers', () => {
        // given
        props.offerer.nOffers = 0

        // when
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )

        // then
        const navLink = screen.getByText('0 offre')
        expect(navLink).not.toHaveAttribute('href')
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
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )

        const navLink = screen.getByText('3 lieux')

        // then
        expect(navLink).toHaveAttribute('href', '/structures/AE/')
      })

      it('should display 0 venue with a link to offerer page', () => {
        // given
        props.offerer.nOffers = 0
        props.offerer.managedVenues = []

        // when
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getByText('0 lieu')

        // then
        expect(navLink).toHaveAttribute('href', '/structures/AE/')
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
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getByText('Nouveau lieu')

        // then
        expect(navLink).toHaveAttribute('href', '/structures/AE/lieux/creation')
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
        render(
          <Provider store={store}>
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getByText('Nouveau lieu')

        // then
        expect(navLink).toHaveAttribute('href', '/erreur/indisponible')
      })
    })
  })
})
