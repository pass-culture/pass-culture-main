import { screen, waitForElementToBeRemoved } from '@testing-library/react'

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
    ).toBeInTheDocument()
  })

  it('should display list of offers for my institution', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [defaultCollectiveOffer] })

    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(defaultCollectiveOffer.name)).toBeInTheDocument()
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
    ).toBeInTheDocument()
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
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Les crédits pass Culture de votre établissement pour la deuxième période de l'année scolaire 2025-2026 ne sont pas encore disponibles. Vous ne pouvez donc pas réserver d'actions payantes. Les réservations d'actions gratuites et les prises de contact avec des partenaires culturels sont toujours possibles./
        )
      ).toBeInTheDocument()
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
})
