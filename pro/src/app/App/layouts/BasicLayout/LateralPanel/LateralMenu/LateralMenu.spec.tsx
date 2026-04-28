import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { LateralMenu } from './LateralMenu'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<LateralMenu isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('LateralMenu', () => {
  it('should not have accessibility violations', async () => {
    const { container } = renderSideNavLinks()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should show a create offer dropdown button with individual and collective choices', async () => {
    renderSideNavLinks({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
            isValidated: true,
          },
        },
      },
    })

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
  it('should display switch venue button with selected venue name', () => {
    const selectedPartnerVenuePublicName = 'Nom public de la structure'

    renderSideNavLinks({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
          },
        },
        user: {
          selectedPartnerVenue: {
            id: 123,
            publicName: selectedPartnerVenuePublicName,
          },
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

  it('should not display switch venue button when no venue is selected', () => {
    renderSideNavLinks({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
          },
        },
        user: {
          selectedPartnerVenue: null,
        },
      },
    })

    expect(
      screen.queryByRole('link', { name: /Changer de structure/ })
    ).not.toBeInTheDocument()
  })
})
