import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { VenueState } from '@/apiClient/v1'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { LateralMenu } from './LateralMenu'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<LateralMenu isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        ...options.storeOverrides?.user,
      },
      ...options.storeOverrides,
    },
    ...options,
  })
}

describe('LateralMenu', () => {
  it('should not have accessibility violations', async () => {
    const { container } = renderSideNavLinks()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should show a create offer dropdown button with individual and collective choices', async () => {
    renderSideNavLinks()

    await userEvent.click(
      screen.getByRole('button', { name: 'Créer une offre' })
    )

    expect(
      screen.getByRole('menuitem', { name: 'Pour le grand public' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('menuitem', { name: 'Pour les groupes scolaires' })
    ).toBeInTheDocument()
  })

  it('should show a disabled create offer button instead of the dropdown when the selected venue is closed', () => {
    renderSideNavLinks({
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            state: VenueState.CLOSED,
          }),
        },
      },
    })

    const createOfferButton = screen.getByRole('button', {
      name: 'Créer une offre',
    })
    expect(createOfferButton).toBeVisible()
    expect(createOfferButton).toBeDisabled()
    expect(createOfferButton).not.toHaveAttribute('aria-haspopup')
  })

  it('should display switch venue button with selected venue name', () => {
    const selectedPartnerVenuePublicName = 'Nom public de la structure'

    renderSideNavLinks({
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 123,
            publicName: selectedPartnerVenuePublicName,
          }),
        },
      },
    })

    const switchVenueButton = screen.getByRole('link', {
      name: `Changer de structure (actuellement sélectionnée : ${selectedPartnerVenuePublicName})`,
    })
    expect(switchVenueButton).toBeInTheDocument()
    expect(switchVenueButton).toHaveAttribute('href', '/hub')
    expect(
      screen.getByRole('link', {
        name: new RegExp(selectedPartnerVenuePublicName),
      })
    ).toBeInTheDocument()
  })

  it('should hide partner page link when the selected venue has no partner page', () => {
    renderSideNavLinks({
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            hasPartnerPage: false,
          }),
        },
      },
    })

    expect(
      screen.queryByRole('link', { name: /Page sur l’application/ })
    ).not.toBeInTheDocument()
  })

  it('should show partner page link when the selected venue has a partner page', async () => {
    renderSideNavLinks({
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            hasPartnerPage: true,
          }),
        },
      },
    })

    const individualSection = screen.getByRole('button', {
      name: /Individuel/,
    })
    await userEvent.click(individualSection) // Open the section

    expect(
      screen.getByRole('link', { name: /Page sur l’application/ })
    ).toBeInTheDocument()
  })

  it('should show parameters page when tab is selected', () => {
    renderSideNavLinks({
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            hasPartnerPage: true,
          }),
        },
      },
    })
    const parametersTab = screen.getByRole('link', { name: 'Paramètres' })
    expect(parametersTab).toBeInTheDocument()
    expect(parametersTab).toHaveAttribute('href', '/parametres')
  })
})
