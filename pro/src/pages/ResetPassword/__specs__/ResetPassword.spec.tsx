import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { ResetPassword } from '../ResetPassword'

vi.mock('commons/utils/recaptcha', () => ({
  initReCaptchaScript: vi.fn(() => ({ remove: vi.fn() })),
  getReCaptchaToken: vi.fn(),
}))

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    postNewPassword: vi.fn(),
  },
}))

const renderLostPassword = (url: string) => {
  renderWithProviders(<ResetPassword />, {
    initialRouterEntries: [url],
  })
}

describe('ResetPassword', () => {
  it('should be able to reset the password when token is ok', async () => {
    const url = '/mot-de-passe-perdu?token=ABC'

    renderLostPassword(url)

    await userEvent.type(
      screen.getByLabelText(/Nouveau mot de passe/),
      'MyN3wP4$$w0rd'
    )
    await userEvent.click(screen.getByText(/Valider/))

    expect(await screen.findByText(/Mot de passe changé !/)).toBeInTheDocument()
    expect(screen.getByText(/Se connecter/)).toBeInTheDocument()
  })

  it('should display bad token informations', async () => {
    vi.spyOn(api, 'postNewPassword').mockRejectedValue({})
    const url = '/mot-de-passe-perdu?token=ABC'

    renderLostPassword(url)

    await userEvent.type(
      screen.getByLabelText(/Nouveau mot de passe/),
      'MyN3wP4$$w0rd'
    )
    await userEvent.click(screen.getByText(/Valider/))

    expect(screen.getByText('Ce lien a expiré !')).toBeInTheDocument()
  })
})
