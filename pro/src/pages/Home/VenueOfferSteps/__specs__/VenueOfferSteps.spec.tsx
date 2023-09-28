import { screen } from '@testing-library/react'
import React from 'react'

import { VenueOfferStepsProps } from 'pages/Home/VenueOfferSteps/VenueOfferSteps'
import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueOfferSteps } from '../index'

const renderVenueOfferSteps = (
  props: VenueOfferStepsProps,
  features: any = {}
) => {
  const currentUser = {
    id: 'EY',
  }
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser,
    },
    features,
  }

  return renderWithProviders(<VenueOfferSteps {...props} />, {
    storeOverrides,
    initialRouterEntries: ['/accueil'],
  })
}

describe('VenueOfferSteps', () => {
  const props: VenueOfferStepsProps = {
    hasVenue: false,
    offererId: 1,
  }
  it('Should display venue creation link if user has no venue', async () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer un lieu')).toBeInTheDocument()
  })
  it('Should not display venue creation link if user has venues', async () => {
    props.hasVenue = true
    renderVenueOfferSteps(props)
    expect(screen.queryByText('Créer un lieu')).not.toBeInTheDocument()
  })
  it('Should display offer creation link if user has no offer on venue', async () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
  })
  it('Should display reimbursement link if user has no ReimbursementPoint on venue', async () => {
    props.hasMissingReimbursementPoint = true
    renderVenueOfferSteps(props)
    expect(
      screen.getByText('Renseigner des coordonnées bancaires')
    ).toBeInTheDocument()
  })
  it('Should not display reimbursement link if user has ReimbursementPoint on venue', async () => {
    props.hasMissingReimbursementPoint = false
    renderVenueOfferSteps(props)
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })
  it('Should display eac dms link when condition to display it is true', async () => {
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  it('Should display bank information status follow link when condition to display it is true', async () => {
    props.shouldDisplayEACInformationSection = false
    props.hasPendingBankInformationApplication = true
    props.demarchesSimplifieesApplicationId = 1232799
    renderVenueOfferSteps(props)
    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: 'Suivre mon dossier de coordonnées bancaires',
      })
    ).toHaveAttribute(
      'href',
      'https://www.demarches-simplifiees.fr/dossiers/1232799/messagerie'
    )
  })
  it('Should not display ds application link when the FF is enabled', async () => {
    renderVenueOfferSteps(props, {
      list: [
        { isActive: true, nameKey: 'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY' },
      ],
    })
    expect(screen.queryByText('Démarche en cours :')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Suivre mon dossier de coordonnées bancaires',
      })
    ).not.toBeInTheDocument()
  })

  it('redirect to dms even if there is no dms application id', async () => {
    props.hasVenue = false
    props.shouldDisplayEACInformationSection = false
    props.hasPendingBankInformationApplication = true
    props.demarchesSimplifieesApplicationId = null
    renderVenueOfferSteps(props)
    expect(
      screen.getByRole('link', {
        name: 'Suivre mon dossier de coordonnées bancaires',
      })
    ).toHaveAttribute('href', 'https://www.demarches-simplifiees.fr/dossiers')
  })

  it('Should display link for eac informations if has adage id and already created offer', async () => {
    props.hasVenue = false
    props.hasAdageId = true
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    expect(
      screen.getByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).toBeInTheDocument()
  })

  it('Should display disabled link to eac informations if venue doesnt have adage id', async () => {
    props.hasVenue = false
    props.hasAdageId = false
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    const eacInformationsLink = screen.getByRole('link', {
      name: 'Renseigner mes informations à destination des enseignants',
    })
    expect(eacInformationsLink).toBeInTheDocument()
    expect(eacInformationsLink).toHaveAttribute('aria-disabled')
  })

  it('should not display dms link if condition to display it is false', async () => {
    props.hasVenue = false
    props.shouldDisplayEACInformationSection = false
    renderVenueOfferSteps(props)
    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should not display venueOfferSteps if no condition to display informations', async () => {
    props.hasCreatedOffer = true
    props.hasPendingBankInformationApplication = false
    props.shouldDisplayEACInformationSection = false
    renderVenueOfferSteps(props)
    expect(screen.queryByText('Prochaines étapes :')).not.toBeInTheDocument()
    expect(screen.queryByTestId('venue-offer-steps')).not.toBeInTheDocument()
    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should display venueOfferSteps if condition to display it', async () => {
    props.hasCreatedOffer = true
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    expect(screen.getByText('Prochaines étapes :')).toBeInTheDocument()
  })
})
