import { screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
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
  dmsStatus = DMSApplicationstatus.EN_CONSTRUCTION,
  dmsInProgress = false,
  hasAdageId = false,
  adageInscriptionDate = '',
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
      dmsStatus={dmsStatus}
      dmsInProgress={dmsInProgress}
      hasCreatedOffer={hasCreatedOffer}
      hasAdageId={hasAdageId}
      adageInscriptionDate={adageInscriptionDate}
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
  it('Should display section procedure in progress if user has procedure in progress', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      dmsInProgress: true,
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
      dmsInProgress: true,
      hasCreatedOffer: true,
      dmsStatus: DMSApplicationstatus.ACCEPTE,
    })
    expect(
      screen.getByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).toBeInTheDocument()
  })

  it('Should not display link for eac informations if status procedure is refused ', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: false,
      dmsStatus: DMSApplicationstatus.REFUSE,
    })
    expect(
      screen.queryByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).not.toBeInTheDocument()
  })
  it('should not display eac informations section if has adage id for more than 30 days', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: true,
      adageInscriptionDate: addDays(new Date(), -31).toISOString(),
      dmsStatus: DMSApplicationstatus.ACCEPTE,
    })
    expect(
      screen.queryByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).not.toBeInTheDocument()
  })
  it('should not display dms timeline if button has adage id for more than 30 days', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: true,
      adageInscriptionDate: addDays(new Date(), -31).toISOString(),
      dmsStatus: DMSApplicationstatus.ACCEPTE,
    })
    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })
  it('should not display dms timeline if dms application is refused', async () => {
    renderVenueOfferSteps({
      hasVenue: false,
      hasAdageId: false,
      dmsStatus: DMSApplicationstatus.REFUSE,
    })
    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })
})
