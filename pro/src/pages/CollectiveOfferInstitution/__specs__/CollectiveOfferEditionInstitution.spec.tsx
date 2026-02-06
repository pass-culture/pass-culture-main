import { screen } from '@testing-library/react'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferEditionInstitution } from '../CollectiveOfferEditionInstitution'

vi.mock('@/apiClient/api', () => ({
  api: {
    getEducationalInstitutions: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferEditionInstitution = (
  path: string,
  storeOverride?: any
) => {
  renderWithProviders(<CollectiveOfferEditionInstitution {...defaultProps} />, {
    initialRouterEntries: [path],
    storeOverrides: storeOverride,
  })
}

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferEditionInstitution', () => {
  it('should render collective offer institution form', async () => {
    renderCollectiveOfferEditionInstitution('/offre/A1/collectif/etablissement')

    expect(
      await screen.findByRole('heading', {
        name: /Modifier l’offre/,
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()
  })
})
