import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { apiNew } from '@/apiClient/api'
import { RECAPTCHA_ERROR } from '@/commons/core/shared/constants'
import * as utils from '@/commons/utils/recaptcha'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { LostPassword } from './LostPassword'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
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
      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser/ })
      )

      // he has been redirected to next step
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: /Vous allez recevoir un email/ })
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
        screen.getByRole('heading', {
          name: 'Réinitialisez votre mot de passe',
        })
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          'Entrez votre email pour recevoir un lien de réinitialisation.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Réinitialiser' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: 'Retour à la connexion' })
      ).toBeInTheDocument()

      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.tab()
      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser/ })
      )
      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: /Vous allez recevoir un email/ })
        ).toBeInTheDocument()
      })
    })

    it('should call resetPassword again when user resend email', async () => {
      // given
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)

      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')

      renderLostPassword()

      // first submit
      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )

      await userEvent.tab()

      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser/ })
      )

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: /Vous allez recevoir un email/ })
        ).toBeInTheDocument()
      })

      // when
      await userEvent.click(
        screen.getByRole('button', { name: 'Renvoyer un nouveau lien' })
      )

      // then
      await waitFor(() => {
        expect(apiNew.resetPassword).toHaveBeenCalledTimes(2)
      })

      expect(apiNew.resetPassword).toHaveBeenNthCalledWith(1, {
        body: {
          token: 'token',
          email: 'coucou@example.com',
        },
      })

      expect(apiNew.resetPassword).toHaveBeenNthCalledWith(2, {
        body: {
          token: 'token',
          email: 'coucou@example.com',
        },
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
      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser/ })
      )

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
      await userEvent.click(
        screen.getByRole('button', { name: /Réinitialiser/ })
      )

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { name: /Vous allez recevoir un email/ })
        ).toBeInTheDocument()
      })

      // then
      await userEvent.click(
        screen.getByRole('button', { name: 'Renvoyer un nouveau lien' })
      )

      await waitFor(() => {
        expect(screen.getByText('Email envoyé.')).toBeInTheDocument()
      })
    })
  })
})
