import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as Notifications } from './Notifications'

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenueWithData: vi.fn() }),
}))

vi.mock('@/apiClient/api', () => ({
  apiNew: { editVenue: vi.fn(), getVenue: vi.fn() },
}))

const renderNotifications = (
  venueOverrides: Partial<GetVenueResponseModel> = {},
  options?: RenderWithProvidersOptions
) => {
  const user = sharedCurrentUserFactory()

  const venue = { ...defaultGetVenue, ...venueOverrides }

  return renderWithProviders(<Notifications />, {
    user,
    ...options,
    storeOverrides: {
      user: { currentUser: user, selectedPartnerVenue: venue },
      ...options?.storeOverrides,
    },
  })
}

describe('Notifications', () => {
  it('should render the notifications section with the email field', async () => {
    renderNotifications()

    expect(
      await screen.findByText('Notifications de réservations')
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Adresse email')).toBeInTheDocument()
  })

  it('should render the save button', async () => {
    renderNotifications()

    expect(
      await screen.findByRole('button', { name: /Enregistrer/ })
    ).toBeInTheDocument()
  })

  it('should update the email field when the user types', async () => {
    renderNotifications({ bookingEmail: '' })

    const emailField = await screen.findByLabelText('Adresse email')
    await userEvent.type(emailField, 'new@test.com')

    expect(emailField).toHaveValue('new@test.com')
  })
})
