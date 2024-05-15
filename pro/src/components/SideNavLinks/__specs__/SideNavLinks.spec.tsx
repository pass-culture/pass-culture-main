import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { SideNavLinks } from '../SideNavLinks'

const renderSideNavLinks = (options: RenderWithProvidersOptions = {}) => {
  renderWithProviders(<SideNavLinks isLateralPanelOpen={true} />, {
    initialRouterEntries: ['/'],
    user: sharedCurrentUserFactory({ hasPartnerPage: true }),
    ...options,
  })
}

describe('SideNavLinks', () => {
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

  it('should not display partner link if user as no parnter page', () => {
    renderSideNavLinks({
      user: sharedCurrentUserFactory({ hasPartnerPage: false }),
    })

    expect(screen.queryByText('Page sur l’application')).not.toBeInTheDocument()
  })
})
