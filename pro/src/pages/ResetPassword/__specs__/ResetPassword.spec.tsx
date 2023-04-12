import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'utils/renderWithProviders'

import ResetPassword from '../ResetPassword'

jest.mock('utils/recaptcha', () => ({
  initReCaptchaScript: jest.fn().mockReturnValue({ remove: jest.fn() }),
  getReCaptchaToken: jest.fn().mockResolvedValue({}),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
    postNewPassword: jest.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = (url: string) => {
  renderWithProviders(<ResetPassword />, {
    initialRouterEntries: [url],
  })
}

describe('ResetPassword', () => {
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
      await userEvent.click(screen.getByText(/Valider/))

      // he has been redirected to final step
      expect(
        await screen.findByText(/Mot de passe changé !/)
      ).toBeInTheDocument()
      expect(screen.getByText(/Se connecter/)).toBeInTheDocument()
    })

    it('should display bad token informations', async () => {
      // given
      jest.spyOn(api, 'postNewPassword').mockRejectedValue({})
      const url = '/mot-de-passe-perdu?token=ABC'

      // when
      renderLostPassword(url)

      // then
      // user can fill and submit new password
      await userEvent.type(
        screen.getByLabelText(/Nouveau mot de passe/),
        'MyN3wP4$$w0rd'
      )
      await userEvent.click(screen.getByText(/Valider/))

      // he has been redirected to final step
      expect(screen.getByText('Ce lien a expiré !')).toBeInTheDocument()
    })
  })
})
