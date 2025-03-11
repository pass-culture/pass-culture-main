import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, describe, expect } from 'vitest'
import { axe } from 'vitest-axe'

import { api } from 'apiClient/api'
import * as useMediaQuery from 'commons/hooks/useMediaQuery'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { SideNavLinks } from '../SideNavLinks'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<SideNavLinks isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('SideNavLinks', () => {
  it('should not have accessibility violations', async () => {
    const { container } = renderSideNavLinks()
    expect(await axe(container)).toHaveNoViolations()
  })
  it('should toggle individual section on individual section button click', async () => {
    renderSideNavLinks()

    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(
      screen.queryByRole('link', { name: 'Guichet' })
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(screen.getByRole('link', { name: 'Guichet' })).toBeInTheDocument()
  })

  it('should toggle collective section on collective section button click', async () => {
    renderSideNavLinks()

    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
    expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(1)
    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
    expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(2)
  })

  it('should show template offers link in collective offer section link when FF is enabled', async () => {
    renderSideNavLinks({
      features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'],
    })

    // close individual section
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))

    expect(
      screen.getByRole('link', { name: 'Offres vitrines' })
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Offres' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Réservations' })
    ).toBeInTheDocument()
  })

  it('should not show template offers link in collective offer section link when FF is disabled', async () => {
    renderSideNavLinks()

    // close individual section
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))

    expect(
      screen.queryByRole('link', { name: 'Offres vitrines' })
    ).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Offres' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Réservations' })
    ).toBeInTheDocument()
  })

  it('should display partner link if user as partner page', async () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      hasPartnerPage: true,
      managedVenues: [
        { ...defaultGetOffererVenueResponseModel, isPermanent: true, id: 17 },
      ],
    })

    renderSideNavLinks({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
        },
        offerer: currentOffererFactory(),
      },
    })

    expect(
      await screen.findByText('Page sur l’application')
    ).toBeInTheDocument()
  })

  it('should not display partner link if user as no partner page', () => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      hasPartnerPage: false,
    })

    renderSideNavLinks({
      user: sharedCurrentUserFactory(),
    })

    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })

  it('should not display create offre button if offerer is not validated', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({})

    renderSideNavLinks({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
        },
        offerer: currentOffererFactory(),
      },
      user: sharedCurrentUserFactory(),
    })

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalled()
    })

    expect(
      screen.queryByRole('link', { name: 'Créer une offre' })
    ).not.toBeInTheDocument()
  })

  describe('small height devices', () => {
    beforeEach(() => {
      vi.spyOn(useMediaQuery, 'useMediaQuery').mockReturnValue(true)
    })

    it('should collapse menus', () => {
      renderSideNavLinks()

      const individualAccordionButton = screen.getByRole('button', {
        name: 'Individuel',
      })
      expect(individualAccordionButton).toBeInTheDocument()
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).not.toBeInTheDocument()
    })

    it('should collapse one menu at a time', async () => {
      renderSideNavLinks()

      const individualAccordionButton = screen.getByRole('button', {
        name: 'Individuel',
      })
      const collectiveAccordionButton = screen.getByRole('button', {
        name: 'Collectif',
      })

      await userEvent.click(individualAccordionButton)
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).toBeInTheDocument()
      await userEvent.click(collectiveAccordionButton)
      expect(
        screen.queryByRole('link', { name: 'Guichet' })
      ).not.toBeInTheDocument()
    })
  })
})
