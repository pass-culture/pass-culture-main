import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import LostPassword from '../LostPassword'

jest.mock('repository/pcapi/pcapi', () => ({}))
jest.mock('utils/recaptcha', () => ({
  initReCaptchaScript: jest.fn().mockReturnValue({ remove: jest.fn() }),
  getReCaptchaToken: jest.fn().mockResolvedValue({}),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
    postNewPassword: jest.fn().mockResolvedValue({}),
    resetPassword: jest.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = (url: string) => {
  renderWithProviders(<LostPassword />, {
    initialRouterEntries: [url],
  })
}

describe('src | components | pages | LostPassword', () => {
  describe('when user arrive on reset password page', () => {
    it('should be able to sent his email', async () => {
      // given
      const url = '/mot-de-passe-perdu'

      // when
      renderLostPassword(url)

      // then
      // user can fill and submit email
      await userEvent.type(
        screen.getByLabelText(/Adresse e-mail/),
        'coucou@example.com'
      )
      await userEvent.click(screen.getByText(/Valider/))

      // he has been redirected to next step
      expect(screen.getByText(/Merci/)).toBeInTheDocument()
    })
  })

  describe('when user arrive from his reset password link', () => {
    it('should be able to sent his password', async () => {
      // given
      const url = '/mot-de-passe-perdu?token=ABC'

      // when
      renderLostPassword(url)

      // then
      // user can fill and submit new password
      await userEvent.type(
        screen.getByLabelText(/Nouveau mot de passe/),
        'MyN3wP4$$w0rd'
      )
      await userEvent.click(screen.getByText(/Envoyer/))

      // he has been redirected to final step
      expect(
        await screen.findByText(/Mot de passe changé !/)
      ).toBeInTheDocument()
      expect(screen.getByText(/Se connecter/)).toBeInTheDocument()
    })
  })
})
