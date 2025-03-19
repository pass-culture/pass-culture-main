import { screen } from '@testing-library/react'

import { api } from 'apiClient/api'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { managedVenueFactory, userOffererFactory } from 'commons/utils/factories/userOfferersFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { MandatoryCollectiveOfferFromParamsProps } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferSummaryCreation } from './CollectiveOfferSummaryCreation'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    requestId: vi.fn(),
    requete: '1',
  }),
  useNavigate: vi.fn(),
  default: vi.fn(),
}))

vi.mock('apiClient/api', () => ({
  api: {
    listEducationalOfferers: vi.fn(),
    getCategories: vi.fn(),
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

const renderCollectiveOfferSummaryCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferSummaryCreation {...props} />, {
    ...options,
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: getCollectiveOfferFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferSummaryCreation', () => {
  const venue = managedVenueFactory({ id: 1 })
  const offerer = userOffererFactory({
    id: 1,
    name: 'Ma super structure',
    managedVenues: [venue],
  })

  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'getCollectiveOffer')
    vi.spyOn(api, 'getCollectiveOfferTemplate')
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [offerer],
    })
  })

  it('should render collective offer summary ', async () => {
    renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )
    expect(
      await screen.findByRole('heading', {
        name: /Créer une offre/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Détails de l’offre',
      })
    ).toBeInTheDocument()
  })

  it('should have requete parameter in the link for previous step when requete is present in the URL', async () => {
    renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    const previousStepLink = await screen.findByText('Retour')
    expect(previousStepLink.getAttribute('href')).toBe(
      '/offre/1/collectif/visibilite?requete=1'
    )
  })

  it('should display the saved information in the action bar', async () => {
    renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    expect(await screen.findByText('Brouillon enregistré')).toBeInTheDocument()

    expect(screen.getByText('Enregistrer et continuer')).toBeInTheDocument()
  })

  it('should render bookable offer summary creation with three edit links (details, stock, institution)', async () => {
    renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    expect(await screen.findAllByText('Modifier')).toHaveLength(3)
  })

  it('should render template offer summary creation with one edit link', async () => {
    const templateProps = {
      offer: getCollectiveOfferTemplateFactory(),
      isTemplate: true,
      offerer: undefined,
    }

    renderCollectiveOfferSummaryCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      templateProps
    )

    expect(await screen.findAllByText('Modifier')).toHaveLength(1)
  })
})
