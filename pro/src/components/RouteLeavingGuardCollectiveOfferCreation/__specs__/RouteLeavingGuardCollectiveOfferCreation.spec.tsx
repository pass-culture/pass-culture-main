import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'
import type { Store } from 'redux'

import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import RouteLeavingGuardCollectiveOfferCreation, {
  RouteLeavingGuardCollectiveOfferCreationProps,
} from '../RouteLeavingGuardCollectiveOfferCreation'

const renderRouteLeavingGuardCollectiveOfferCreation = async (
  props: RouteLeavingGuardCollectiveOfferCreationProps,
  history: History,
  store = configureTestStore({})
) => {
  render(
    <Provider store={store}>
      <Router history={history}>
        <Link to="/about">About</Link>
        <Link to={`/offre/creation/collective`}>Création</Link>
        <Link to={`/offre/AE/collective/stocks`}>Stocks</Link>
        <Link to={`/offre/AE/collectif/visibilite`}>Visibilité</Link>
        <Link to={`/offre/AE/collective/confirmation`}>Confirmation</Link>
        <RouteLeavingGuardCollectiveOfferCreation {...props} />
      </Router>
    </Provider>
  )
}

describe('components | RouteLeavingGuardCollectiveOfferCreation', () => {
  const props: RouteLeavingGuardCollectiveOfferCreationProps = { when: true }
  const history = createBrowserHistory()

  describe('when following creation flow', () => {
    it('should not display confirmation modal when following creation flow', async () => {
      history.push('/offre/creation/collectif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)

      history.push('/offre/AE/collectif/stocks')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/visibilite')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/creation/recapitulatif')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/confirmation')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when following template creation flow - FF OFF', async () => {
      history.push('/offre/creation/collectif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)

      history.push('/offre/AE/collectif/stocks')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/T-AE/collectif/creation/recapitulatif')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/T-AE/collectif/confirmation')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when following template creation flow - FF ON', async () => {
      history.push('/offre/creation/collectif')
      const store = configureTestStore({
        features: {
          list: [
            {
              isActive: true,
              nameKey: 'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION',
            },
          ],
        },
      })
      renderRouteLeavingGuardCollectiveOfferCreation(props, history, store)

      history.push('/offre/AE/collectif/vitrine/creation/recapitulatif')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/vitrine/confirmation')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when following duplication flow', async () => {
      history.push('/offre/duplication/collectif/PU')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)

      history.push('/offre/duplication/collectif/AE/stocks')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/duplication/collectif/AE/visibilite')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/duplication/collectif/AE/recapitulatif')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/confirmation')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })

  describe('when leaving creation flow', () => {
    it('should display confirmation modal when leaving offer creation', () => {
      history.push('/offre/creation/collectif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving stock creation', () => {
      history.push('/offre/AE/collectif/stocks')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving visibility creation', () => {
      history.push('/offre/AE/collectif/visibilite')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving summary creation', () => {
      history.push('/offre/AE/collectif/creation/recapitulatif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should not display confirmation modal when leaving confirmation page', () => {
      history.push('/offre/AE/collectif/confirmation')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should display confirmation modal when leaving offer creation', () => {
      history.push('/offre/duplication/collectif/PU')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving stock creation', () => {
      history.push('/offre/duplication/collectif/AE/stocks')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving visibility creation', () => {
      history.push('/offre/duplication/collectif/AE/visibilite')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })

    it('should display confirmation modal when leaving summary creation', () => {
      history.push('/offre/duplication/collectif/AE/recapitulatif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
    })
  })

  describe('when going backward', () => {
    describe('with FF OFF', () => {
      it('should display confirmation modal when going from stocks to offer creation', () => {
        history.push('/offre/AE/collectif/stocks')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/creation/collectif')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should display confirmation modal when going from visibility to stocks creation', () => {
        history.push('/offre/AE/collectif/visibilite')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/AE/collectif/stocks')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should display confirmation modal when going from summary to visibility creation', () => {
        history.push('/offre/AE/collectif/creation/recapitulatif')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/AE/collectif/visibilite')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should display confirmation modal when going from summary to stocks creation', () => {
        history.push('/offre/T-AE/collectif/creation/recapitulatif')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/AE/collectif/stocks')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should redirect to collective offers page when going from confirmation to summary', () => {
        history.push('/offre/AE/collectif/confirmation')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/AE/collectif/creation/recapitulatif')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).not.toBeInTheDocument()
        expect(window.location.pathname).toBe('/offres/collectives')
      })

      it('should display confirmation modal when going from stocks to offer creation', () => {
        history.push('/offre/duplication/collectif/AE/stocks')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/duplication/collectif/PU')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should display confirmation modal when going from visibility to stocks creation', () => {
        history.push('/offre/duplication/collectif/AE/visibilite')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/duplication/collectif/AE/stocks')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })

      it('should display confirmation modal when going from summary to visibility creation', () => {
        history.push('/offre/duplication/collectif/AE/recapitulatif')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history)
        history.push('/offre/duplication/collectif/AE/visibilite')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).toBeInTheDocument()
      })
    })

    describe('with FF ON', () => {
      let store: Store<RootState>

      beforeAll(() => {
        store = configureTestStore({
          features: {
            list: [
              {
                isActive: true,
                nameKey: 'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION',
              },
            ],
          },
        })
      })

      it('should not display confirmation modal when going from stocks to offer creation', () => {
        history.push('/offre/AE/collectif/stocks')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history, store)
        history.push('/offre/creation/collectif')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).not.toBeInTheDocument()
      })

      it('should not display confirmation modal when going from stocks to offer creation with offer id in url', () => {
        history.push('/offre/AE/collectif/stocks')
        renderRouteLeavingGuardCollectiveOfferCreation(props, history, store)
        history.push('/offre/collectif/AE/creation')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).not.toBeInTheDocument()
      })

      it('should not display confirmation modal when going from visibility to stocks', () => {
        history.push('/offre/AE/collectif/visibilite')
        renderRouteLeavingGuardOfferCreation(props, history, store)
        history.push('/offre/AE/collectif/stocks')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).not.toBeInTheDocument()
      })

      it('should not display confirmation modal when going from visibility to offer creation', () => {
        history.push('/offre/AE/collectif/visibilite')
        renderRouteLeavingGuardOfferCreation(props, history, store)
        history.push('/offre/collectif/AE/creation')

        expect(
          screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
        ).not.toBeInTheDocument()
      })
    })
  })
})
