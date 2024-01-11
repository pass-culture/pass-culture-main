import { screen } from '@testing-library/react'
import React from 'react'

import {
  VenueOfferSteps,
  VenueOfferStepsProps,
} from 'pages/Home/VenueOfferSteps/VenueOfferSteps'
import * as venueUtils from 'pages/Home/venueUtils'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/apiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

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
    offerer: { ...defaultGetOffererResponseModel },
  }
  const offererWithoutBankAccount = {
    ...defaultGetOffererResponseModel,
    hasPendingBankAccount: false,
    hasValidBankAccount: false,
    hasNonFreeOffer: false,
  }

  beforeEach(() => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(false)
  })

  it('should display venue creation link if user has no venue', () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer un lieu')).toBeInTheDocument()
  })

  it('should not display venue creation link if user has venues', () => {
    props.hasVenue = true
    renderVenueOfferSteps(props)
    expect(screen.queryByText('Créer un lieu')).not.toBeInTheDocument()
  })

  it('should display offer creation link if user has no offer on venue', () => {
    props.hasVenue = false
    renderVenueOfferSteps(props)
    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
  })

  it('should display reimbursement link if user has no ReimbursementPoint on venue', () => {
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasMissingReimbursementPoint: true,
    }
    renderVenueOfferSteps(props)
    expect(
      screen.getByText('Renseigner des coordonnées bancaires')
    ).toBeInTheDocument()
  })

  it('should not display reimbursement link if user has ReimbursementPoint on venue', () => {
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasMissingReimbursementPoint: false,
    }
    renderVenueOfferSteps(props)
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('should display bank account link on first venue if user has no bank account and no offer on offerer', () => {
    props.offerer = offererWithoutBankAccount
    props.offerer.managedVenues = [
      { ...defaultGetOffererVenueResponseModel, hasCreatedOffer: false },
    ]
    props.isFirstVenue = true
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('should display bank account link on second venue if user has no bank account and no paid offer', () => {
    props.offerer = offererWithoutBankAccount
    props.offerer.managedVenues = [
      { ...defaultGetOffererVenueResponseModel, hasCreatedOffer: false },
    ]
    props.isFirstVenue = false
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(screen.getByText('Ajouter un compte bancaire')).toBeInTheDocument()
    expect(
      screen.queryByText('Renseigner des coordonnées bancaires')
    ).not.toBeInTheDocument()
  })

  it('should not display bank account link on second venue if user has no bank account with paid offer', () => {
    props.offerer = offererWithoutBankAccount
    props.offerer.hasNonFreeOffer = true
    props.offerer.managedVenues = [
      { ...defaultGetOffererVenueResponseModel, hasCreatedOffer: false },
    ]
    props.isFirstVenue = false
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should not display bank account link on first venue if user has bank account', () => {
    props.offerer = offererWithoutBankAccount
    props.offerer.managedVenues = [
      { ...defaultGetOffererVenueResponseModel, hasCreatedOffer: true },
    ]
    props.isFirstVenue = true
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should not display account link if user has bank account on offerer', () => {
    props.offerer = {
      ...defaultGetOffererResponseModel,
      hasValidBankAccount: true,
    }
    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })
    expect(
      screen.queryByText('Ajouter un compte bancaire')
    ).not.toBeInTheDocument()
  })

  it('should display eac dms link when condition to display it is true', () => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(true)
    props.venue = { ...defaultGetOffererVenueResponseModel }

    renderVenueOfferSteps(props)

    expect(screen.getByText('Démarche en cours :')).toBeInTheDocument()
    expect(
      screen.getByText('Suivre ma demande de référencement ADAGE')
    ).toBeInTheDocument()
  })

  it('should display bank information status follow link when condition to display it is true', () => {
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasPendingBankInformationApplication: true,
      demarchesSimplifieesApplicationId: 1232799,
    }
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

  it('should not display ds application link when the FF is enabled', () => {
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
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasPendingBankInformationApplication: true,
      demarchesSimplifieesApplicationId: null,
    }
    renderVenueOfferSteps(props)
    expect(
      screen.getByRole('link', {
        name: 'Suivre mon dossier de coordonnées bancaires',
      })
    ).toHaveAttribute('href', 'https://www.demarches-simplifiees.fr/dossiers')
  })

  it('should display link for eac informations if has adage id and already created offer', () => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(true)
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasAdageId: true,
    }

    renderVenueOfferSteps(props)

    expect(
      screen.getByText(
        'Renseigner mes informations à destination des enseignants'
      )
    ).toBeInTheDocument()
  })

  it('should display disabled link to eac informations if venue doesnt have adage id', () => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(true)
    props.venue = { ...defaultGetOffererVenueResponseModel }
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasAdageId: false,
    }

    renderVenueOfferSteps(props)

    const eacInformationsLink = screen.getByRole('link', {
      name: 'Renseigner mes informations à destination des enseignants',
    })
    expect(eacInformationsLink).toBeInTheDocument()
    expect(eacInformationsLink).toHaveAttribute('aria-disabled')
  })

  it('should not display dms link if condition to display it is false', () => {
    props.hasVenue = false

    renderVenueOfferSteps(props)

    expect(
      screen.queryByText('Suivre ma demande de référencement ADAGE')
    ).not.toBeInTheDocument()
  })

  it('should not display venueOfferSteps if no condition to display informations', () => {
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasCreatedOffer: true,
      hasPendingBankInformationApplication: false,
    }

    renderVenueOfferSteps(props)

    expect(screen.queryByText('Prochaines étapes :')).not.toBeInTheDocument()
    expect(screen.queryByTestId('venue-offer-steps')).not.toBeInTheDocument()
    expect(screen.queryByTestId('home-offer-steps')).not.toBeInTheDocument()
  })

  it('should display venueOfferSteps if condition to display it', () => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(true)
    props.venue = { ...defaultGetOffererVenueResponseModel }
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasCreatedOffer: true,
    }

    renderVenueOfferSteps(props)

    expect(screen.getByText('Prochaines étapes :')).toBeInTheDocument()
  })

  it('should render nothing when all steps are not shown', () => {
    vi.spyOn(
      venueUtils,
      'shouldDisplayEACInformationSectionForVenue'
    ).mockReturnValue(false)
    props.venue = {
      ...defaultGetOffererVenueResponseModel,
      hasCreatedOffer: true,
      hasPendingBankInformationApplication: true,
    }

    renderVenueOfferSteps(props, {
      features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
    })

    expect(screen.queryByText('Prochaines étapes :')).not.toBeInTheDocument()
  })
})
