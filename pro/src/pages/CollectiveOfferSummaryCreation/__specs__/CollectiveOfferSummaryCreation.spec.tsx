import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from 'apiClient/api'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { getCollectiveOfferFactory } from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { CollectiveOfferSummaryCreation } from '../CollectiveOfferSummaryCreation'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    requestId: vi.fn(),
    requete: '1',
  }),
  useNavigate: vi.fn(),
  default: vi.fn(),
}))

const renderCollectiveOfferSummaryCreation = async (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferSummaryCreation {...props} />, {
    ...options,
    initialRouterEntries: [path],
  })
  await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))
}

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferSummaryCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getCollectiveOffer')
    vi.spyOn(api, 'getCollectiveOfferTemplate')
  })

  it('should render collective offer summary ', async () => {
    await renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )
    expect(
      screen.getByRole('heading', {
        name: /Créer une nouvelle offre collective/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Détails de l’offre',
      })
    ).toBeInTheDocument()
  })

  it('should have requete parameter in the link for previous step when requete is present in the URL', async () => {
    await renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    const previousStepLink = screen.getByText('Étape précédente')
    expect(previousStepLink.getAttribute('href')).toBe(
      '/offre/1/collectif/visibilite?requete=1'
    )
  })

  it('should display the saved information in the action bar', async () => {
    await renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps,
      {
        features: ['WIP_ENABLE_COLLECTIVE_DRAFT_OFFERS'],
      }
    )

    expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()

    expect(screen.getByText('Enregistrer et continuer')).toBeInTheDocument()
  })
})
