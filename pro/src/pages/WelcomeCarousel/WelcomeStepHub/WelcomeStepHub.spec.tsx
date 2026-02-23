import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { WelcomeCarouselEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { WelcomeStepHub } from '@/pages/WelcomeCarousel/WelcomeStepHub/WelcomeStepHub'

const mockNavigate = vi.fn()
vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

const renderWelcomeStepHub = (initialPath: string = '/bienvenue') => {
  return renderWithProviders(<WelcomeStepHub />, {
    initialRouterEntries: [initialPath],
  })
}
describe('<WelcomeStepHub />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWelcomeStepHub()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display error when teacher is selected', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderWelcomeStepHub()

    await userEvent.click(screen.getByLabelText(/Personnel enseignant/))
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(
      screen.getByText('Mince, vous êtes au mauvais endroit !')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Retour' }))
    expect(
      screen.getByText('Commençons par identifier votre profil')
    ).toBeInTheDocument()
    expect(screen.getByRole('group', { name: /Vous êtes/ })).not.toHaveValue()
  })

  it.each([
    { label: /Partenaire culturel/, target: 'partenaire-culturel' },
    { label: /Jeune/, target: 'jeune' },
    { label: /Personnel enseignant/, target: 'enseignant' },
  ])(`Should log target %s on submit`, async ({ label, target }) => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    renderWelcomeStepHub()
    await userEvent.click(screen.getByRole('radio', { name: label }))
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockLogEvent).toHaveBeenCalledWith(
      WelcomeCarouselEvents.HAS_CLICKED_USER_TYPE,
      { target }
    )
  })

  describe('navigations', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'location', {
        value: vi.fn(),
        configurable: true,
      })
    })

    afterEach(() => {
      vi.unstubAllGlobals()
    })

    it('should navigate to next page if target is pro user', async () => {
      renderWelcomeStepHub()

      await userEvent.click(screen.getByLabelText(/Partenaire culturel/))
      await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
      await waitFor(() =>
        expect(mockNavigate).toHaveBeenCalledWith('/bienvenue/publics')
      )
    })
    it('should navigate to app if target is teen', async () => {
      renderWelcomeStepHub()

      await userEvent.click(screen.getByLabelText(/Jeune/))
      await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
      expect(window.location.href).toBe(
        'https://passculture.app/creation-compte'
      )
    })
    it('should navigate to adage if target is teacher', async () => {
      const mockLogEvent = vi.fn()
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      renderWelcomeStepHub()

      await userEvent.click(screen.getByLabelText(/Personnel enseignant/))
      await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

      expect(
        screen.getByRole('link', { name: 'Accéder à ADAGE' })
      ).toHaveAttribute(
        'href',
        'https://adage-pr.phm.education.gouv.fr/ds/?entityID=https%3A%2F%2Fadage-pr.phm.education.gouv.fr%2Fsp%2Fmdp&return=https%3A%2F%2Fadage-pr.phm.education.gouv.fr%2Fmdp%2FShibboleth.sso%2FLogin%3FSAMLDS%3D1%26target%3Dss%253Amem%253Af7ae5c254ceec3841749f8747ba4ff685aa80d7e05b232b3d8902796e9d36bab%26authnContextClassRef%3Durn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Aac%253Aclasses%253APasswordProtectedTransport%2520urn%253Aoasis%253Anames%253Atc%253ASAML%253A2.0%253Aac%253Aclasses%253ATimeSyncToken'
      )
      await userEvent.click(
        screen.getByRole('link', { name: 'Accéder à ADAGE' })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        WelcomeCarouselEvents.HAS_CLICKED_ADAGE_LINK
      )
    })
  })
})
