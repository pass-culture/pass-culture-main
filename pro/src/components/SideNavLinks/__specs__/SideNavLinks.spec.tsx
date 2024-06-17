import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import 'html-validate/jest'

import { api } from 'apiClient/api'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SideNavLinks } from '../SideNavLinks'
import { axe } from 'vitest-axe'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  return renderWithProviders(<SideNavLinks isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory({ hasPartnerPage: true }),
    ...options,
  })
}

describe('SideNavLinks', () => {
  it('should render a W3C-valid HTML markup', () => {
    const { container } = renderSideNavLinks()

    expect(container).toHTMLValidate()
  })

  it('should be a11y compliant', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({})

    const { container } = renderSideNavLinks()

    await waitFor(() => {
      expect(api.getOfferer).toHaveBeenCalled()
    })

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

    expect(
      await screen.findByText('Page sur l’application')
    ).toBeInTheDocument()
  })

  it('should not display partner link if user as no partner page', () => {
    renderSideNavLinks({
      user: sharedCurrentUserFactory({ hasPartnerPage: false }),
    })

    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })

  it('should not display create offre button if offerer is not validated', async () => {
    vi.spyOn(api, 'getOfferer').mockRejectedValueOnce({})

    renderSideNavLinks({
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
