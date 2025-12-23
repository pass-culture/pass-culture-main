import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { RECAPTCHA_ERROR } from '@/commons/core/shared/constants'
import * as utils from '@/commons/utils/recaptcha'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { LostPassword } from '../LostPassword'

vi.mock('@/apiClient/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({}),
    resetPassword: vi.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = () => {
  renderWithProviders(
    <>
      <LostPassword />
      <SnackBarContainer />
    </>
  )
}

describe('LostPassword', () => {
  describe('when user arrive on reset password page', () => {
    it('should be able to sent his email', async () => {
      // given
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      // when
      renderLostPassword()

      // then
      // user can fill and submit email
      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.tab()
      await userEvent.click(screen.getByText(/Réinitialiser/))

      // he has been redirected to next step
      await waitFor(() => {
        expect(
          screen.getByText(/Vous allez recevoir un email/)
        ).toBeInTheDocument()
      })
    })

    it('should display the right texts', async () => {
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      renderLostPassword()
      expect(
        screen.getByText('Réinitialisez votre mot de passe')
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          'Entrez votre email pour recevoir un lien de réinitialisation.'
        )
      ).toBeInTheDocument()
      expect(screen.getByText('Réinitialiser')).toBeInTheDocument()
      expect(screen.getByText('Retour à la connexion')).toBeInTheDocument()

      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.tab()
      await userEvent.click(screen.getByText(/Réinitialiser/))
      await waitFor(() => {
        expect(
          screen.getByText(/Vous allez recevoir un email/)
        ).toBeInTheDocument()
      })
    })
  })

  describe('when an error occurs', () => {
    it('should display error message when RECAPTCHA_ERROR occurs', async () => {
      // given
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockRejectedValue(RECAPTCHA_ERROR)

      // when
      renderLostPassword()
      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.tab()
      await userEvent.click(screen.getByText(/Réinitialiser/))

      // then
      await waitFor(() => {
        expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
      })
    })
  })

  describe('when email has been sent', () => {
    it('should be able to resend email', async () => {
      // given
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      // when
      renderLostPassword()
      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.tab()
      await userEvent.click(screen.getByText(/Réinitialiser/))

      await waitFor(() => {
        expect(
          screen.getByText(/Vous allez recevoir un email/)
        ).toBeInTheDocument()
      })

      // then
      await userEvent.click(screen.getByText('cliquez ici'))

      await waitFor(() => {
        expect(screen.getByText('Email envoyé.')).toBeInTheDocument()
      })
    })
  })
})
