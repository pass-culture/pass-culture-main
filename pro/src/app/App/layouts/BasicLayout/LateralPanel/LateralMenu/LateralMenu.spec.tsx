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

  describe('with WIP_SWITCH_VENUE feature flag', () => {
    const features = ['WIP_SWITCH_VENUE']

    it('should display switch venue button with selected venue name', () => {
      const selectedVenuePublicName = 'Nom public de la structure'

      renderSideNavLinks({
        storeOverrides: {
          offerer: {
            currentOfferer: {
              ...defaultGetOffererResponseModel,
            },
          },
          user: {
            selectedVenue: { id: 123, publicName: selectedVenuePublicName },
          },
        },
        features,
      })

      const switchVenueButton = screen.getByRole('link', {
        name: `Changer de structure (actuellement sélectionnée : ${selectedVenuePublicName})`,
      })
      expect(switchVenueButton).toBeInTheDocument()
      expect(switchVenueButton).toHaveAttribute('href', '/hub')
      expect(
        screen.getByRole('link', { name: new RegExp(selectedVenuePublicName) })
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
            selectedVenue: null,
          },
        },
        features,
      })

      expect(
        screen.queryByRole('link', { name: /Changer de structure/ })
      ).not.toBeInTheDocument()
    })
  })

  it('should not display switch venue button when WIP_SWITCH_VENUE feature flag is disabled', () => {
    renderSideNavLinks({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            ...defaultGetOffererResponseModel,
          },
        },
        user: {
          selectedVenue: { id: 123, name: 'Test Venue' },
        },
      },
      features: [],
    })

    expect(
      screen.queryByRole('link', { name: /Changer de structure/ })
    ).not.toBeInTheDocument()
  })
})
