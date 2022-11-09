import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'

import { configureTestStore } from 'store/testUtils'

import RouteLeavingGuardOfferIndividual, {
  RouteLeavingGuardOfferIndividualV2Props,
} from '../RouteLeavingGuardOfferIndividualV2'

const stepsUrls: { [key: string]: string } = {
  offer: '/offre/individuel/creation',
  offer_with_id: '/offre/AE/individuel/creation',
  stocks: '/offre/AE/individuel/creation/stocks',
  summary: '/offre/AE/individuel/creation/recapitulatif',
  confirmation: '/offre/AE/individuel/creation/confirmation',
}

const renderRouteLeavingGuard = async (
  props: RouteLeavingGuardOfferIndividualV2Props,
  history: History,
  storeOverride = {}
) => {
  const store = configureTestStore(storeOverride)
  return render(
    <Provider store={store}>
      <Router history={history}>
        <Link to="/about">About</Link>
        <Link to={stepsUrls['offer']}>Création</Link>
        <Link to={stepsUrls['offer_with_id']}>Création with offer</Link>
        <Link to={stepsUrls['stocks']}>Stocks</Link>
        <Link to={stepsUrls['summary']}>Récapitulatif</Link>
        <Link to={stepsUrls['confirmation']}>Confirmation</Link>
        <RouteLeavingGuardOfferIndividual {...props} />
      </Router>
    </Provider>
  )
}

describe('components | RouteLeavingGuardOfferIndividual', () => {
  let props: RouteLeavingGuardOfferIndividualV2Props
  let history: History

  beforeEach(() => {
    props = { when: true }
    history = createBrowserHistory()
  })

  describe('from offer form', () => {
    it('should display confirmation modal when exiting creation funnel', async () => {
      history.push(stepsUrls['offer'])
      const spyHistory = jest.spyOn(history, 'push')
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('About'))
      expect(
        await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
      await userEvent.click(screen.getByText('Quitter'))
      expect(spyHistory).toHaveBeenLastCalledWith(
        expect.objectContaining({ pathname: '/offres' })
      )
    })

    it('should display a confirmation for lost unsaved changes', async () => {
      history.push(stepsUrls['offer'])
      const spyHistory = jest.spyOn(history, 'push')
      renderRouteLeavingGuard(props, history, {
        features: {
          list: [{ isActive: true, nameKey: 'OFFER_DRAFT_ENABLED' }],
        },
      })
      await userEvent.click(screen.getByText('About'))
      expect(
        await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
      expect(
        screen.getByText('Les informations non enregistrées seront perdues.')
      ).toBeInTheDocument()
      await userEvent.click(screen.getByText('Quitter'))
      expect(spyHistory).toHaveBeenLastCalledWith(
        expect.objectContaining({ pathname: '/offres' })
      )
    })

    it('should not display confirmation modal when going to stocks', async () => {
      history.push(stepsUrls['offer'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Stocks'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to summary', async () => {
      history.push(stepsUrls['offer'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to confirmation', async () => {
      history.push(stepsUrls['offer'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Confirmation'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })

  describe('from stocks form', () => {
    it('should display confirmation modal when exiting creation funnel', async () => {
      history.push(stepsUrls['stocks'])
      const spyHistory = jest.spyOn(history, 'push')
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('About'))
      expect(
        await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
      ).toBeInTheDocument()
      await userEvent.click(screen.getByText('Quitter'))
      expect(spyHistory).toHaveBeenLastCalledWith(
        expect.objectContaining({ pathname: '/about' })
      )
    })

    it('should not display confirmation modal when going to offer', async () => {
      history.push(stepsUrls['stocks'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to offer with id', async () => {
      history.push(stepsUrls['stocks'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création with offer'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to summary', async () => {
      history.push(stepsUrls['stocks'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to confirmation', async () => {
      history.push(stepsUrls['stocks'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Confirmation'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })

  describe('from summary page', () => {
    it('should not display confirmation modal when exiting creation funnel', async () => {
      history.push(stepsUrls['summary'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('About'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to offer', async () => {
      history.push(stepsUrls['summary'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to offer with id', async () => {
      history.push(stepsUrls['summary'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création with offer'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to stock', async () => {
      history.push(stepsUrls['summary'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Stocks'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to confirmation', async () => {
      history.push(stepsUrls['summary'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Confirmation'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })

  describe('from confirmation page', () => {
    it('should not display confirmation modal when exiting creation funnel', async () => {
      history.push(stepsUrls['confirmation'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('About'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to offer', async () => {
      history.push(stepsUrls['confirmation'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to offer with id', async () => {
      history.push(stepsUrls['confirmation'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Création with offer'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to stock', async () => {
      history.push(stepsUrls['confirmation'])
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Stocks'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going to summary', async () => {
      history.push(stepsUrls['confirmation'])
      const spyHistory = jest.spyOn(history, 'push')
      renderRouteLeavingGuard(props, history)
      await userEvent.click(screen.getByText('Récapitulatif'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
      expect(spyHistory).toHaveBeenLastCalledWith(
        expect.objectContaining({ pathname: '/offres' })
      )
    })
  })
})
