import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'

import { api } from 'apiClient/api'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { ResetPassword } from './ResetPassword'

vi.mock('commons/utils/recaptcha', () => ({
  initReCaptchaScript: vi.fn(() => ({ remove: vi.fn() })),
  getReCaptchaToken: vi.fn(),
}))

vi.mock('apiClient/api', () => ({
  api: {
    getProfile: vi.fn(),
    postNewPassword: vi.fn(),
    postCheckToken: vi.fn(),
  },
}))

const mockUseNavigate = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: () => mockUseNavigate,
}))

const mockUseNotification = {
  error: vi.fn(),
  success: vi.fn(),
}
vi.mock('commons/hooks/useNotification', async () => ({
  ...(await vi.importActual('commons/hooks/useNotification')),
  useNotification: () => mockUseNotification,
}))

const renderLostPassword = (url: string, features: string[] = []) => {
  renderWithProviders(
    <Routes>
      <Route path="/demande-mot-de-passe/:token" element={<ResetPassword />} />
    </Routes>,
    {
      initialRouterEntries: [url],
      features,
    }
  )
}

describe('ResetPassword', () => {
  it('should be able to reset the password when token is ok', async () => {
    const url = '/demande-mot-de-passe/ABC'

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
    const url = '/demande-mot-de-passe/ABC'

    renderLostPassword(url)

    await userEvent.type(
      screen.getByLabelText(/Nouveau mot de passe/),
      'MyN3wP4$$w0rd'
    )
    await userEvent.click(screen.getByText(/Valider/))

    expect(screen.getByText('Ce lien a expiré !')).toBeInTheDocument()
  })

  describe('with FF WIP_2025_SIGN_UP', () => {
    it('should be able to reset the password when token is ok', async () => {
      const url = '/demande-mot-de-passe/ABC'

      vi.spyOn(api, 'postCheckToken').mockResolvedValue()

      renderLostPassword(url, ['WIP_2025_SIGN_UP'])

      await userEvent.type(
        await screen.findByLabelText(/Nouveau mot de passe/),
        'MyN3wP4$$w0rd'
      )
      await userEvent.type(
        await screen.findByLabelText(/Confirmez votre nouveau mot de passe/),
        'MyN3wP4$$w0rd'
      )
      await userEvent.click(screen.getByText('Confirmer'))

      expect(mockUseNotification.success).toHaveBeenCalledWith(
        'Mot de passe modifié.'
      )
      expect(mockUseNavigate).toHaveBeenCalledWith('/connexion')
    })

    it('should immediately redirect to login page if token is missing', async () => {
      const url = '/demande-mot-de-passe/toto'

      vi.spyOn(api, 'postCheckToken').mockRejectedValue({
        token: ['Mauvais token'],
      })

      renderLostPassword(url, ['WIP_2025_SIGN_UP'])

      await vi.waitFor(() => {
        expect(mockUseNotification.error).toHaveBeenCalledWith(
          'Le lien est invalide ou a expiré. Veuillez recommencer.'
        )
        expect(mockUseNavigate).toHaveBeenCalledWith('/demande-mot-de-passe')
      })
    })

    it('should immediately redirect to login page if token is invalid', async () => {
      const url = '/demande-mot-de-passe/ABC'

      vi.spyOn(api, 'postCheckToken').mockRejectedValue({
        token: ['Votre lien de changement de mot de passe est invalide.'],
      })

      renderLostPassword(url, ['WIP_2025_SIGN_UP'])

      await vi.waitFor(() => {
        expect(mockUseNotification.error).toHaveBeenCalledWith(
          'Le lien est invalide ou a expiré. Veuillez recommencer.'
        )
        expect(mockUseNavigate).toHaveBeenCalledWith('/demande-mot-de-passe')
      })
    })
  })
})
