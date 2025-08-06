import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { apiAdage } from '@/apiClient/api'
import {
  defaultAdageUser,
  defaultCollectiveOffer,
} from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { AdageUserContextProvider } from '@/pages/AdageIframe/app/providers/AdageUserContext'

import { OffersForMyInstitution } from '../OffersForMyInstitution'

vi.mock('@/apiClient/api', () => ({
  apiAdage: {
    getCollectiveOffersForMyInstitution: vi.fn(),
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
    { features: features }
  )
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
})
