import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from 'apiClient/api'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SideNavLinks } from '../SideNavLinks'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<SideNavLinks isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory({ hasPartnerPage: true }),
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

    expect(
      screen.queryByRole('link', { name: 'Guichet' })
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(screen.getByRole('link', { name: 'Guichet' })).toBeInTheDocument()
  })

  it('should toggle collective section on collective section button click', async () => {
    renderSideNavLinks()

    expect(screen.queryAllByRole('link', { name: 'Offres' })).toHaveLength(0)
    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
    expect(screen.getAllByRole('link', { name: 'Offres' })).toHaveLength(1)
  })

  it('should show template offers link in collective offer section link when FF is enabled', async () => {
    renderSideNavLinks({
      features: ['WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'],
    })

    expect(
      screen.queryByRole('link', { name: 'Offres vitrines' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('link', { name: 'Offres vitrines' })
    ).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))
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

    await userEvent.click(screen.getByRole('button', { name: 'Collectif' }))

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
      managedVenues: [
        { ...defaultGetOffererVenueResponseModel, isPermanent: true, id: 17 },
      ],
    })
    renderSideNavLinks({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory({ hasPartnerPage: true }),
          selectedOffererId: 1,
        },
      },
    })
    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(
      await screen.findByText('Page sur l’application')
    ).toBeInTheDocument()
  })

  it('should not display partner link if user as no partner page', async () => {
    renderSideNavLinks({
      user: sharedCurrentUserFactory({ hasPartnerPage: false }),
    })
    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Individuel' }))
    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })

  it('should not display create offre button if offerer is not validated', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({})

    renderSideNavLinks({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory({ hasPartnerPage: false }),
          selectedOffererId: 1,
        },
      },
      user: sharedCurrentUserFactory({ hasPartnerPage: false }),
    })

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalled()
    })

    expect(
      screen.queryByRole('link', { name: 'Créer une offre' })
    ).not.toBeInTheDocument()
  })
})
