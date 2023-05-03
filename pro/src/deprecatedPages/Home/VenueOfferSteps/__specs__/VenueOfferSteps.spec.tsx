import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueOfferSteps } from '../index'

jest.mock('hooks/useActiveFeature', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(true),
}))

const renderVenueOfferSteps = ({
  hasVenue = false,
  hasCreatedOffer = false,
  hasMissingReimbursementPoint = true,
  hasAdageId = false,
  shouldDisplayEACInformationSection = false,
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
      offererId={12}
      hasMissingReimbursementPoint={hasMissingReimbursementPoint}
      hasCreatedOffer={hasCreatedOffer}
      hasAdageId={hasAdageId}
      shouldDisplayEACInformationSection={shouldDisplayEACInformationSection}
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
  it('Should display eac dms link when condition to display it is true', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      shouldDisplayEACInformationSection: true,
    })
    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  it('Should display link for eac informations if has adage id and already created offer', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: true,
      shouldDisplayEACInformationSection: true,
    })
    expect(
      screen.getByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).toBeInTheDocument()
  })

  it('Should display disabled link to eac informations if venue doesnt have adage id', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: false,
      shouldDisplayEACInformationSection: true,
    })
    const eacInformationsLink = screen.getByRole('link', {
      name: 'Renseigner mes informations à destination des enseignants',
    })
    expect(eacInformationsLink).toBeInTheDocument()
    expect(eacInformationsLink).toHaveAttribute('aria-disabled')
  })

  it('should not display dms link if condition to display it is false', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      shouldDisplayEACInformationSection: false,
    })
    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })
})
