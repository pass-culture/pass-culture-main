import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import VenueItem from '../VenueItem'

describe('src | components | pages | OffererCreation | VenueItem', () => {
  let props
  let history
  let store

  beforeEach(() => {
    store = configureTestStore({})
    props = {
      venue: {
        id: 'AAA',
        managingOffererId: 'ABC',
        name: 'fake name',
        publicName: null,
      },
    }
    history = createBrowserHistory()
  })

  describe('render', () => {
    describe('venue name link', () => {
      it('should render link to see venue details with venue name when no public name provided', () => {
        // given
        render(
          <Provider store={store}>
            <Router history={history}>
              <VenueItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[0]

        // then
        expect(navLink).toHaveTextContent('fake name')
        expect(navLink).toHaveAttribute('href', '/structures/ABC/lieux/AAA')
      })

      it('should render link to see venue details with venue public name when public name provided', () => {
        // given
        props.venue.publicName = 'fake public name'

        // when
        render(
          <Provider store={store}>
            <Router history={history}>
              <VenueItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[0]

        // then
        expect(navLink).toHaveTextContent('fake public name')
      })
    })

    describe('create new offer in the venue link', () => {
      it('should redirect to offer creation page', () => {
        render(
          <Provider store={store}>
            <Router history={history}>
              <VenueItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[1]

        // then
        expect(navLink).toHaveTextContent('Créer une offre')
        expect(navLink).toHaveAttribute(
          'href',
          '/offre/creation?lieu=AAA&structure=ABC'
        )
      })
    })

    describe('see venue details link', () => {
      it('should redirect to venue details page', () => {
        render(
          <Provider store={store}>
            <Router history={history}>
              <VenueItem {...props} />
            </Router>
          </Provider>
        )
        const navLink = screen.getAllByRole('link')[2]
        // then
        expect(navLink).toHaveAttribute('href', '/structures/ABC/lieux/AAA')
      })
    })
  })
})
