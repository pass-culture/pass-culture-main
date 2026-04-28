import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

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
  if (!options?.storeOverrides?.offerer) {
    options = {
      ...options,
      storeOverrides: {
        ...options?.storeOverrides,
        user: {
          ...options?.storeOverrides?.user,
          venues: baseVenues,
        },
      },
      features: [],
    }
  }
  renderWithProviders(<HeaderDropdown />, options)
}

describe('App', () => {
  it('should give access to profile page', async () => {
    renderHeaderDropdown()

    await userEvent.click(screen.getByTestId('profile-button'))
    const profileLink = screen.getByRole('link', { name: /voir mon profil/i })

    expect(profileLink).toHaveAttribute('href', '/profil')
  })
})
