import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { scrollToTop } from '../GeneralInformation/commons/utils/scrollToTop'
import { useSave } from './commons/hooks/useSave'
import { Component as Notifications } from './Notifications'

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenueWithData: vi.fn() }),
}))

vi.mock('@/apiClient/api', () => ({
  api: { editVenue: vi.fn(), getVenue: vi.fn() },
}))

vi.mock('./commons/hooks/useSave', () => ({
  useSave: vi.fn(() => ({ save: vi.fn() })),
}))
vi.mock('../GeneralInformation/commons/utils/scrollToTop', () => ({
  scrollToTop: vi.fn(),
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

  it('should call useSave and scrollToTop on save', async () => {
    const saveMock = vi.fn()
    const scrollToTopMock = vi.fn()

    vi.mocked(useSave).mockReturnValue({ save: saveMock })
    vi.mocked(scrollToTop).mockImplementation(scrollToTopMock)

    renderNotifications()

    const emailField = await screen.findByLabelText('Adresse email')
    await userEvent.clear(emailField)
    await userEvent.type(emailField, 'new@test.com')
    await userEvent.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(saveMock).toHaveBeenCalledTimes(1)
    expect(scrollToTopMock).toHaveBeenCalledTimes(1)
  })

  it('should update the email field when the user types', async () => {
    renderNotifications({ bookingEmail: '' })

    const emailField = await screen.findByLabelText('Adresse email')
    await userEvent.type(emailField, 'new@test.com')

    expect(emailField).toHaveValue('new@test.com')
  })

  it('should reset the form when clicking Annuler', async () => {
    renderNotifications({ bookingEmail: 'initial@test.com' })

    const emailField = await screen.findByLabelText('Adresse email')
    await userEvent.clear(emailField)
    await userEvent.type(emailField, 'changed@test.com')

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(emailField).toHaveValue('initial@test.com')
  })
})
