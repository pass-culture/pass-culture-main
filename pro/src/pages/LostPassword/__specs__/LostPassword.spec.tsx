import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as utils from 'commons/utils/recaptcha'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { LostPassword } from '../LostPassword'

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn().mockResolvedValue({}),
    resetPassword: vi.fn().mockResolvedValue({}),
  },
}))

const renderLostPassword = (url: string) => {
  renderWithProviders(<LostPassword />, {
    initialRouterEntries: [url],
  })
}

describe('LostPassword', () => {
  describe('when user arrive on reset password page', () => {
    it('should be able to sent his email', async () => {
      // given
      vi.spyOn(utils, 'initReCaptchaScript').mockReturnValue({
        remove: vi.fn(),
      } as unknown as HTMLScriptElement)
      vi.spyOn(utils, 'getReCaptchaToken').mockResolvedValue('token')
      const url = '/demande-mot-de-passe'

      // when
      renderLostPassword(url)

      // then
      // user can fill and submit email
      await userEvent.type(
        screen.getByLabelText(/Adresse email */),
        'coucou@example.com'
      )
      await userEvent.click(screen.getByText(/Valider/))

      // he has been redirected to next step
      expect(screen.getByText(/Merci/)).toBeInTheDocument()
    })
  })
})
