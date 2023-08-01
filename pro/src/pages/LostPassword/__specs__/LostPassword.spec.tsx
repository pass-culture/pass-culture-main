import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ResetPassword from '../LostPassword'

vi.mock('utils/recaptcha', () => ({
  initReCaptchaScript: vi.fn().mockReturnValue({ remove: vi.fn() }),
  getReCaptchaToken: vi.fn().mockResolvedValue({}),
}))

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({}),
    resetPassword: vi.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = (url: string) => {
  renderWithProviders(<ResetPassword />, {
    initialRouterEntries: [url],
  })
}

describe('LostPassword', () => {
  describe('when user arrive on reset password page', () => {
    it('should be able to sent his email', async () => {
      // given
      const url = '/demande-mot-de-passe'

      // when
      renderLostPassword(url)

      // then
      // user can fill and submit email
      await userEvent.type(
        screen.getByLabelText(/Adresse email/),
        'coucou@example.com'
      )
      await userEvent.click(screen.getByText(/Valider/))

      // he has been redirected to next step
      expect(screen.getByText(/Merci/)).toBeInTheDocument()
    })
  })
})
