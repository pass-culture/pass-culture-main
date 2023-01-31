import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueOfferSteps } from '../index'

const renderVenueOfferSteps = ({
  hasVenue = false,
  hasMissingReimbursementPoint = true,
}) => {
  const currentUser = {
    id: 'EY',
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
  }

  return renderWithProviders(
    <VenueOfferSteps
      hasVenue={hasVenue}
      offererId="AB"
      hasMissingReimbursementPoint={hasMissingReimbursementPoint}
    />,
    { storeOverrides, initialRouterEntries: ['/accueil'] }
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
  it('Should display reimbursement link if user has no ReimbursementPoint on venue', async () => {
    renderVenueOfferSteps({ hasVenue: false })
    expect(
      screen.getByText('Renseigner des coordonnées bancaires')
    ).toBeInTheDocument()
  })
  it('Should not display reimbursement link if user has ReimbursementPoint on venue', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasMissingReimbursementPoint: false,
    })
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })
})
