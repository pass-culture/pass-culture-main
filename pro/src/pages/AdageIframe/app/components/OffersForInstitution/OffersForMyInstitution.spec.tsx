import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { AdageFrontRoles } from '@/apiClient/adage/new'
import { apiAdage } from '@/apiClient/api'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
} from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { OffersForMyInstitution } from './OffersForMyInstitution'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    getCollectiveOffersForMyInstitution: vi.fn(),
    getEducationalInstitutionWithBudget: vi.fn(),
    saveRedactorPreferences: vi.fn(),
  },
}))

const renderOffersForMyInstitution = (
  user = defaultAdageUser,
  features?: string[]
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <OffersForMyInstitution />
    </AdageUserContextProvider>,
    { features }
  )
}

const budgetResponse = {
  budget: 0,
  city: 'Paris',
  id: 1,
  institutionType: '',
  name: 'Lycée Jean Moulin',
  phoneNumber: '0111111111',
  postalCode: '75000',
}

describe('OffersInstitutionList', () => {
  it('should display no result page', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [] })

    renderOffersForMyInstitution({ ...defaultAdageUser, offersCount: 0 })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByText('Vous n’avez pas d’offre à préréserver')
    ).toBeVisible()
  })

  it('should display list of offers for my institution', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [defaultCollectiveOffer] })

    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(defaultCollectiveOffer.name)).toBeVisible()
  })

  it('should show an offer card', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [defaultCollectiveOffer] })

    renderOffersForMyInstitution(defaultAdageUser)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByRole('link', { name: defaultCollectiveOffer.name })
    ).toBeVisible()
  })

  describe('budget banner', () => {
    it('should display budget exhaustion banner when institution has no budget to spend', async () => {
      vi.spyOn(
        apiAdage,
        'getEducationalInstitutionWithBudget'
      ).mockResolvedValueOnce(budgetResponse)
      renderOffersForMyInstitution(defaultAdageUser)

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(
        screen.getByText('Informations sur les crédits 2026')
      ).toBeVisible()
      expect(
        screen.getByText(
          /Les crédits pass Culture de votre établissement pour la deuxième période de l'année scolaire 2025-2026 ne sont pas encore disponibles. Vous ne pouvez donc pas réserver d'actions payantes. Les réservations d'actions gratuites et les prises de contact avec des partenaires culturels sont toujours possibles./
        )
      ).toBeVisible()
    })

    it('should not display budget exhaustion banner when institution has budget to spend', async () => {
      vi.spyOn(
        apiAdage,
        'getEducationalInstitutionWithBudget'
      ).mockResolvedValueOnce({ ...budgetResponse, budget: 1000 })
      renderOffersForMyInstitution(defaultAdageUser)

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(
        screen.queryByText('Informations sur les crédits 2026')
      ).not.toBeInTheDocument()
    })
  })

  describe('survey satisfaction', () => {
    it('should display survey satisfaction', async () => {
      renderOffersForMyInstitution(defaultAdageUser)

      const surveySatisfaction = await screen.findByText(
        'Enquête de satisfaction'
      )
      expect(surveySatisfaction).toBeVisible()
    })

    it('should not display survey satisfaction if user role readonly', () => {
      renderOffersForMyInstitution({
        ...defaultAdageUser,
        role: AdageFrontRoles.READONLY,
      })

      const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
      expect(surveySatisfaction).not.toBeInTheDocument()
    })

    it('should not display survey satisfaction', () => {
      renderOffersForMyInstitution({
        ...defaultAdageUser,
        preferences: { feedback_form_closed: true },
      })

      const surveySatisfaction = screen.queryByText('Enquête de satisfaction')
      expect(surveySatisfaction).not.toBeInTheDocument()
    })
  })
})
