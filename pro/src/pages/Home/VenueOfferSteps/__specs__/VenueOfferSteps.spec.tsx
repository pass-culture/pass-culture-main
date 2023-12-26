import { screen } from '@testing-library/react'
import React from 'react'

import { VenueOfferStepsProps } from 'pages/Home/VenueOfferSteps/VenueOfferSteps'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { VenueOfferSteps } from '../index'

const renderVenueOfferSteps = (
  props: VenueOfferStepsProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<VenueOfferSteps {...props} />, {
    initialRouterEntries: ['/accueil'],
    ...options,
  })
}

describe('VenueOfferSteps', () => {
  const props: VenueOfferStepsProps = {
    hasVenue: false,
    offererId: 1,
    offererHasBankAccount: false,
  }

  it('Should display venue creation link if user has no venue', () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer un lieu')).toBeInTheDocument()
  })

  it('Should not display venue creation link if user has venues', () => {
    props.hasVenue = true
    renderVenueOfferSteps(props)
    expect(screen.queryByText('Créer un lieu')).not.toBeInTheDocument()
  })

  it('Should display offer creation link if user has no offer on venue', () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
  })

  it('Should display reimbursement link if user has no ReimbursementPoint on venue', () => {
    props.hasMissingReimbursementPoint = true
    renderVenueOfferSteps(props)
    expect(
      screen.getByText('Renseigner des coordonnées bancaires')
    ).toBeInTheDocument()
  })

  it('Should not display reimbursement link if user has ReimbursementPoint on venue', () => {
    props.hasMissingReimbursementPoint = false
    renderVenueOfferSteps(props)
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('Should display bank account link on first venue if user has no bank account and no offer on offerer', () => {
    props.offererHasBankAccount = false
    props.offererHasCreatedOffer = false
    props.isFirstVenue = true
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('Should display bank account link on second venue if user has no bank account and no paid offer', () => {
    props.offererHasBankAccount = false
    props.offererHasCreatedOffer = false
    props.hasNonFreeOffer = false
    props.isFirstVenue = false
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('Should not display bank account link on second venue if user has no bank account with paid offer', () => {
    props.offererHasBankAccount = false
    props.offererHasCreatedOffer = false
    props.hasNonFreeOffer = true
    props.isFirstVenue = false
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('Should not display bank account link on first venue if user has bank account', () => {
    props.offererHasBankAccount = false
    props.offererHasCreatedOffer = true
    props.isFirstVenue = true
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('Should not display account link if user has bank account on offerer', () => {
    props.offererHasBankAccount = true
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('Should display eac dms link when condition to display it is true', () => {
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  it('Should display bank information status follow link when condition to display it is true', () => {
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

  it('Should not display ds application link when the FF is enabled', () => {
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(screen.queryByText('Démarche en cours :')).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Suivre mon dossier de coordonnées bancaires',
      })
    ).not.toBeInTheDocument()
  })

  it('redirect to dms even if there is no dms application id', () => {
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

  it('Should display link for eac informations if has adage id and already created offer', () => {
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

  it('Should display disabled link to eac informations if venue doesnt have adage id', () => {
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

  it('should not display dms link if condition to display it is false', () => {
    props.hasVenue = false
    props.shouldDisplayEACInformationSection = false
    renderVenueOfferSteps(props)
    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should not display venueOfferSteps if no condition to display informations', () => {
    props.venueHasCreatedOffer = true
    props.hasPendingBankInformationApplication = false
    props.shouldDisplayEACInformationSection = false
    renderVenueOfferSteps(props)
    expect(screen.queryByText('Prochaines étapes :')).not.toBeInTheDocument()
    expect(screen.queryByTestId('venue-offer-steps')).not.toBeInTheDocument()
    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should display venueOfferSteps if condition to display it', () => {
    props.venueHasCreatedOffer = true
    props.shouldDisplayEACInformationSection = true
    renderVenueOfferSteps(props)
    expect(screen.getByText('Prochaines étapes :')).toBeInTheDocument()
  })
})
