import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'
import { axe } from 'vitest-axe'

import { makeVenueListItemLiteResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { HeaderDropdown } from './HeaderDropdown'

vi.mock('@/apiClient/api', () => ({
  api: {
    signout: vi.fn(),
  },
}))
const baseVenues = [
  makeVenueListItemLiteResponseModel({
    id: 3,
    managingOffererId: 1,
    name: 'Digital Venue A1',
  }),
  makeVenueListItemLiteResponseModel({
    id: 4,
    managingOffererId: 2,
    name: 'Digital Venue B1',
  }),
]
const renderHeaderDropdown = (options?: RenderWithProvidersOptions) => {
  options = {
    ...options,
    storeOverrides: {
      ...options?.storeOverrides,
      user: {
        ...options?.storeOverrides?.user,
        venues: baseVenues,
      },
    },
    features: options?.features ?? [],
  }
  return renderWithProviders(<HeaderDropdown />, options)
}

describe('App', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderHeaderDropdown({
      features: ['WIP_ENABLE_PRO_DARK_MODE'],
    })

    await userEvent.click(screen.getByTestId('profile-button'))

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not render the color theme toggle when the feature is disabled', async () => {
    renderHeaderDropdown()

    await userEvent.click(screen.getByTestId('profile-button'))

    expect(
      screen.queryByRole('group', { name: 'Thème' })
    ).not.toBeInTheDocument()
  })

  it('should render the color theme toggle when the feature is enabled', async () => {
    renderHeaderDropdown({ features: ['WIP_ENABLE_PRO_DARK_MODE'] })

    await userEvent.click(screen.getByTestId('profile-button'))

    expect(screen.getByRole('group', { name: 'Thème' })).toBeInTheDocument()
  })

  it('should close the menu when pressing Escape from the color theme toggle', async () => {
    renderHeaderDropdown({ features: ['WIP_ENABLE_PRO_DARK_MODE'] })

    await userEvent.click(screen.getByTestId('profile-button'))
    await userEvent.click(screen.getByRole('button', { name: 'Thème sombre' }))
    await userEvent.keyboard('{Escape}')

    expect(screen.getByTestId('header-dropdown-menu-div')).toHaveAttribute(
      'aria-hidden',
      'true'
    )
    expect(screen.getByTestId('profile-button')).toHaveFocus()
  })

  it('should render profile menu text semantically in the structure signup funnel', async () => {
    renderHeaderDropdown({
      initialRouterEntries: ['/inscription/structure/recherche'],
    })

    await userEvent.click(screen.getByTestId('profile-button'))

    expect(screen.getByText('Profil').tagName).toBe('P')
    expect(
      screen.queryByRole('link', { name: /voir mon profil/i })
    ).not.toBeInTheDocument()

    const logoutButton = screen.getByRole('button', { name: 'Se déconnecter' })
    expect(logoutButton.querySelector('span')).toHaveTextContent(
      'Se déconnecter'
    )
  })

  it('should give access to profile page', async () => {
    renderHeaderDropdown()

    expect(screen.getByTestId('header-dropdown-menu-div')).toHaveAttribute(
      'aria-hidden',
      'true'
    )

    await userEvent.click(screen.getByTestId('profile-button'))
    const profileLink = screen.getByRole('link', { name: /voir mon profil/i })

    expect(profileLink).toHaveAttribute('href', '/profil')
    expect(screen.getByTestId('header-dropdown-menu-div')).toHaveAttribute(
      'aria-hidden',
      'false'
    )

    await userEvent.keyboard('{Escape}')

    expect(screen.getByTestId('header-dropdown-menu-div')).toHaveAttribute(
      'aria-hidden',
      'true'
    )

    await userEvent.click(screen.getByTestId('profile-button'))
    await userEvent.click(document.body)

    expect(screen.getByTestId('header-dropdown-menu-div')).toHaveAttribute(
      'aria-hidden',
      'true'
    )
  })
})
