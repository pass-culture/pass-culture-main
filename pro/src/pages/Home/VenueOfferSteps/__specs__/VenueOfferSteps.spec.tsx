import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import { VenueOfferSteps } from '../index'

const renderVenueOfferSteps = ({
  hasVenue = false,
  hasOffer = false,
  hasMissingReimbursementPoint = true,
}) => {
  const currentUser = {
    id: 'EY',
  }
  const store = configureTestStore({
    user: {
      initialized: true,
      currentUser,
    },
  })
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/accueil']}>
        <VenueOfferSteps
          hasVenue={hasVenue}
          offererId="AB"
          hasOffer={hasOffer}
          hasMissingReimbursementPoint={hasMissingReimbursementPoint}
        />
      </MemoryRouter>
    </Provider>
  )
}

describe('VenueOfferSteps', () => {
  it('Should display venue creation link if user has no venue', async () => {
    renderVenueOfferSteps({ hasVenue: false })
    expect(screen.getByText('Créer un lieu')).toBeInTheDocument()
  })
  it('Should not display venue creation link if user has venues', async () => {
    renderVenueOfferSteps({ hasVenue: true })
    expect(screen.queryByText('Créer un lieu')).not.toBeInTheDocument()
  })
  it('Should display offer creation link if user has no offer on venue', async () => {
    renderVenueOfferSteps({ hasVenue: false })
    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
  })
  it('Should display not offer creation link if user has an offer on venue', async () => {
    renderVenueOfferSteps({ hasVenue: false, hasOffer: true })
    expect(screen.queryByText('Créer une offre')).not.toBeInTheDocument()
  })
  it('Should display reimbursement link if user has no ReimbursementPoint on venue', async () => {
    renderVenueOfferSteps({ hasVenue: false })
    expect(
      screen.getByText('Renseigner des coordonnées bancaires')
    ).toBeInTheDocument()
  })
  it('Should not display reimbursement link if user has ReimbursementPoint on venue', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasOffer: false,
      hasMissingReimbursementPoint: false,
    })
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })
})
