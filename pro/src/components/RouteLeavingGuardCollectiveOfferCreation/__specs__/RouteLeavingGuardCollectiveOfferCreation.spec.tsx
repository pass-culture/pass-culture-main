import { screen } from '@testing-library/react'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'

import { renderWithProviders } from 'utils/renderWithProviders'

import RouteLeavingGuardCollectiveOfferCreation, {
  RouteLeavingGuardCollectiveOfferCreationProps,
} from '../RouteLeavingGuardCollectiveOfferCreation'

const renderRouteLeavingGuardCollectiveOfferCreation = async (
  props: RouteLeavingGuardCollectiveOfferCreationProps,
  history: History
) => {
  renderWithProviders(
    <Router history={history}>
      <Link to="/about">About</Link>
      <Link to={`/offre/creation/collective`}>Création</Link>
      <Link to={`/offre/AE/collective/stocks`}>Stocks</Link>
      <Link to={`/offre/AE/collectif/visibilite`}>Visibilité</Link>
      <Link to={`/offre/AE/collective/confirmation`}>Confirmation</Link>
      <RouteLeavingGuardCollectiveOfferCreation {...props} />
    </Router>
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

    it('should not display confirmation modal when following template creation flow', async () => {
      history.push('/offre/creation/collectif')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)

      history.push('/offre/AE/collectif/vitrine/creation/recapitulatif')
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()

      history.push('/offre/AE/collectif/vitrine/confirmation')
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
  })

  describe('when going backward', () => {
    it('should not display confirmation modal when going from stocks to offer creation', () => {
      history.push('/offre/AE/collectif/stocks')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/offre/creation/collectif')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going from stocks to offer creation with offer id in url', () => {
      history.push('/offre/AE/collectif/stocks')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/offre/collectif/AE/creation')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going from visibility to stocks', () => {
      history.push('/offre/AE/collectif/visibilite')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/offre/AE/collectif/stocks')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })

    it('should not display confirmation modal when going from visibility to offer creation', () => {
      history.push('/offre/AE/collectif/visibilite')
      renderRouteLeavingGuardCollectiveOfferCreation(props, history)
      history.push('/offre/collectif/AE/creation')

      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })
})
