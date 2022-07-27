import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'

import RouteLeavingGuardOfferCreation, {
  RouteLeavingGuardOfferCreationProps,
} from '../RouteLeavingGuardOfferCreation'

const renderRouteLeavingGuardOfferCreation = async (
  props: RouteLeavingGuardOfferCreationProps,
  history: History
) => {
  render(
    <Router history={history}>
      <Link to="/about">About</Link>
      <Link to={'/offre/individuel/creation'}>Création</Link>
      <Link to={'/offre/AE/individuel/creation/stocks'}>Stocks</Link>
      <Link to={'/offre/AE/individuel/creation/confirmation'}>
        Confirmation
      </Link>
      <RouteLeavingGuardOfferCreation {...props} />
    </Router>
  )
}

describe('new_components | RouteLeavingGuardOfferCreation', () => {
  let props: RouteLeavingGuardOfferCreationProps
  const history = createBrowserHistory()

  beforeEach(() => {
    props = {}
  })

  it('should display confirmation modal before changing page', async () => {
    history.push('/')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('About'))
    expect(
      await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
    ).toBeInTheDocument()
  })

  it('should reditect to offers list without confirmation modal when going from confirmation to stock', async () => {
    history.push('/offre/AE/individuel/creation/confirmation')
    const spyHistory = jest.spyOn(history, 'push')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('Stocks'))
    expect(
      screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
    ).not.toBeInTheDocument()
    expect(spyHistory).toHaveBeenLastCalledWith({ pathname: '/offres' })
  })

  it('should reditect to offers list with confirmation modal when going from stock to creation', async () => {
    history.push('/offre/AE/individuel/creation/stocks')
    const spyHistory = jest.spyOn(history, 'push')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('Création'))
    expect(
      await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Quitter'))
    expect(spyHistory).toHaveBeenLastCalledWith(
      expect.objectContaining({ pathname: '/offres' })
    )
  })

  it('should display confirmation modal when going from stock to offer creation', async () => {
    history.push('/offre/AE/individuel/stocks')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('Création'))
    expect(
      await screen.findByText(/Voulez-vous quitter la création d’offre ?/)
    ).toBeInTheDocument()
  })

  it('should not display confirmation modal when going to stock', async () => {
    history.push('/offre/creation/individuel')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('Stocks'))
    expect(
      screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
    ).not.toBeInTheDocument()
  })

  it('should not display confirmation modal when going to confirmation', async () => {
    history.push('/offre/AE/individuel/stocks')
    renderRouteLeavingGuardOfferCreation(props, history)
    await userEvent.click(screen.getByText('Confirmation'))
    expect(
      screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
    ).not.toBeInTheDocument()
  })

  describe('CollectiveOffer', () => {
    beforeEach(() => {
      props.isCollectiveFlow = true
    })

    it('should not display confirmation modal when going to visibilité', async () => {
      history.push('/')
      render(
        <Router history={history}>
          <Link to="/about">About</Link>
          <Link to={`/offre/creation/collective`}>Création</Link>
          <Link to={`/offre/AE/collective/stocks`}>Stocks</Link>
          <Link to={`/offre/AE/collectif/visibilite`}>Visibilité</Link>
          <Link to={`/offre/AE/collective/confirmation`}>Confirmation</Link>
          <RouteLeavingGuardOfferCreation {...props} />
        </Router>
      )
      await userEvent.click(screen.getByText('Visibilité'))
      expect(
        screen.queryByText(/Voulez-vous quitter la création d’offre ?/)
      ).not.toBeInTheDocument()
    })
  })
})
