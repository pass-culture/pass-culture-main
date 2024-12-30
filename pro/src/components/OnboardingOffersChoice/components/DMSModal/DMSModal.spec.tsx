import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as router from 'react-router-dom'
import { axe } from 'vitest-axe'

import { api } from 'apiClient/api'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { DMSModal } from './DMSModal'

const renderDMSModal = (options?: RenderWithProvidersOptions) => {
  return renderWithProviders(<DMSModal />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: { selectedOffererId: 1, offererNames: [] },
    },
    user: sharedCurrentUserFactory(),
    ...options,
  })
}

describe('<DMSModal />', () => {
  it('should render correctly', async () => {
    renderDMSModal()

    expect(
      await screen.findByRole('heading', { name: /Quelles sont les étapes ?/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('link', { name: /Déposer un dossier/ })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
    ).toBeInTheDocument()
  })

  it('should not have accessibility violations', async () => {
    const { container } = renderDMSModal()

    expect(await axe(container)).toHaveNoViolations()
  })

  describe('API calls', () => {
    vi.mock('react-router-dom', async () => ({
      ...(await vi.importActual('react-router-dom')),
      useNavigate: vi.fn(),
    }))

    vi.mock('apiClient/api', () => ({
      api: {
        getOffererEligibility: vi.fn(),
      },
    }))

    it('should request the API when clicking on "J’ai déposé un dossier"', async () => {
      renderDMSModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(api.getOffererEligibility).toHaveBeenCalledOnce()
    })

    it('should redirect to the homepage if user is onboarded', async () => {
      const mockNavigate = vi.fn()
      vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
      vi.spyOn(api, 'getOffererEligibility').mockResolvedValue({
        offererId: 1,
        isOnboarded: true,
      })

      renderDMSModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(mockNavigate).toHaveBeenCalledWith('/accueil')
    })

    it('should show an error message if user is not onboarded', async () => {
      vi.spyOn(api, 'getOffererEligibility').mockResolvedValue({
        offererId: 1,
        isOnboarded: false,
      })

      renderDMSModal()

      await userEvent.click(
        await screen.findByRole('button', { name: /J’ai déposé un dossier/ })
      )

      expect(
        await screen.findByText('Un problème est survenu, veuillez réessayer')
      ).toBeInTheDocument()
    })
  })
})
