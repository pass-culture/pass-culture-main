import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import type { History } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import type { Store } from 'redux'

import { configureTestStore } from 'store/testUtils'

import OfferBreadcrumb, { OfferBreadcrumbStep } from '../OfferBreadcrumb'

describe('src | new_components | OfferBreadcrumb', () => {
  let store: Store
  let history: History

  beforeEach(() => {
    history = createBrowserHistory()
  })

  describe('Individual offer', () => {
    beforeEach(() => {
      store = configureTestStore({})
    })

    it('should display breadcrumb for individual offer in creation', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={true}
              offerId="A1"
              isOfferEducational={false}
            />
          </Provider>
        </Router>
      )

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(3)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
      expect(listItems[2]).toHaveTextContent('Confirmation')
    })

    it('should display breadcrumb for individual offer in edition', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={false}
              offerId="A1"
              isOfferEducational={false}
            />
          </Provider>
        </Router>
      )

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(2)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Stocks et prix')
    })

    it('should generate link with offerId when user is editing an offer', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={false}
              offerId="A1"
              isOfferEducational={false}
            />
          </Provider>
        </Router>
      )

      const linkItems = await screen.findAllByRole('link')

      expect(linkItems).toHaveLength(2)
      expect(linkItems[0].getAttribute('href')).toBe(
        '/offre/A1/individuel/edition'
      )
      expect(linkItems[1].getAttribute('href')).toBe(
        '/offre/A1/individuel/stocks'
      )
    })
  })

  describe('Collective offer - with domain association', () => {
    beforeEach(() => {
      store = configureTestStore({})
    })

    it('should display breadcrumb for collective offer - with visibility step', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={true}
              offerId="A1"
              isOfferEducational={true}
            />
          </Provider>
        </Router>
      )

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Date et prix')
      expect(listItems[2]).toHaveTextContent('Visibilité')
      expect(listItems[3]).toHaveTextContent('Confirmation')
    })

    it('should generate link with offerId when user is editing an offer', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={false}
              offerId="A1"
              isOfferEducational={true}
            />
          </Provider>
        </Router>
      )

      const linkItems = await screen.findAllByRole('link')

      expect(linkItems).toHaveLength(3)
      expect(linkItems[0].getAttribute('href')).toBe(
        '/offre/A1/collectif/edition'
      )
      expect(linkItems[1].getAttribute('href')).toBe(
        '/offre/A1/collectif/stocks/edition'
      )
      expect(linkItems[2].getAttribute('href')).toBe(
        '/offre/A1/collectif/visibilite/edition'
      )
    })

    it('should not display visibility step if offer is showcase', async () => {
      render(
        <Router history={history}>
          <Provider store={store}>
            <OfferBreadcrumb
              activeStep={OfferBreadcrumbStep.DETAILS}
              isCreatingOffer={false}
              offerId="T-A1"
              isOfferEducational={true}
            />
          </Provider>
        </Router>
      )

      const linkItems = await screen.findAllByRole('link')
      expect(linkItems).toHaveLength(2)
      expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()
    })
  })
})
