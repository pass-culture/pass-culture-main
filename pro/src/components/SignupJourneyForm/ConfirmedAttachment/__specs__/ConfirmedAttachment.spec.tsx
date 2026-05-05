import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ConfirmedAttachment } from '../ConfirmedAttachment'

const mockNavigate = vi.fn()
vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

const renderConfirmedAttachmentScreen = () => {
  return renderWithProviders(<ConfirmedAttachment />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('screens:SignupJourney::ConfirmedAttachment', () => {
  it('should render component', () => {
    renderConfirmedAttachmentScreen()

    expect(screen.getByText('Votre demande a été envoyée')).toBeVisible()
  })

  it('should redirect user on offerer page on continue button click', async () => {
    renderConfirmedAttachmentScreen()

    await userEvent.click(screen.getByText('Accéder à mon espace'))

    // getUserDefaultPath uses `rootStore.getState()` and it isn't overridden.
    // Thus, we only check if navigate is called
    expect(mockNavigate).toHaveBeenCalled()
  })
})
