import { screen } from '@testing-library/react'

import { getCollectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOfferEditionVisibility } from '../CollectiveOfferEditionVisibility'

vi.mock('apiClient/api', () => ({
  api: {
    getEducationalInstitutions: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferEditionVisibility = (
  path: string,
  storeOverride?: any
) => {
  renderWithProviders(<CollectiveOfferEditionVisibility {...defaultProps} />, {
    initialRouterEntries: [path],
    storeOverrides: storeOverride,
  })
}

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferEditionVisibility', () => {
  it('should render collective offer visibility form', async () => {
    renderCollectiveOfferEditionVisibility('/offre/A1/collectif/visibilite')

    expect(
      await screen.findByRole('heading', {
        name: /Éditer une offre collective/,
      })
    ).toBeInTheDocument()

    expect(
      await screen.findByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()
  })
  it('should render new collective offer visibility form if ff active', async () => {
    renderCollectiveOfferEditionVisibility('/offre/A1/collectif/visibilite')

    expect(
      await screen.findByRole('heading', {
        name: "Renseignez l'établissement scolaire et l'enseignant",
      })
    ).toBeInTheDocument()
  })
})
