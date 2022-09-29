import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import LostPassword from '../LostPassword'

jest.mock('repository/pcapi/pcapi', () => ({
  resetPassword: jest.fn().mockResolvedValue({}),
  submitResetPassword: jest.fn().mockResolvedValue({}),
}))
jest.mock('utils/recaptcha', () => ({
  initReCaptchaScript: jest.fn().mockReturnValue({ remove: jest.fn() }),
  getReCaptchaToken: jest.fn().mockResolvedValue({}),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getProfile: jest.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = url => {
  const store = configureTestStore({
    user: {
      currentUser: { id: 'CMOI' },
    },
  })

  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[url]}>
        <LostPassword />
      </MemoryRouter>
    </Provider>
  )
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
      await userEvent.click(screen.getByText(/Envoyer/))

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
      expect(screen.getByText(/Mot de passe changé !/)).toBeInTheDocument()
      expect(screen.getByText(/Se connecter/)).toBeInTheDocument()
    })
  })
})
