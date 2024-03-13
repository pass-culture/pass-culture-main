import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from 'apiClient/api'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import {
  defaultGetVenue,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { CollectiveOfferPreviewCreation } from '../CollectiveOfferPreviewCreation'

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useParams: () => ({
    requestId: vi.fn(),
    requete: '1',
  }),
  useNavigate: vi.fn(),
  default: vi.fn(),
}))

const renderCollectiveOfferPreviewCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferPreviewCreation {...props} />, {
    ...options,
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: getCollectiveOfferTemplateFactory(),
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferPreviewCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)
  })

  it('should render collective offer preview ', async () => {
    renderCollectiveOfferPreviewCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )
    expect(
      screen.getByRole('heading', {
        name: /Créer une nouvelle offre collective/,
      })
    ).toBeInTheDocument()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: defaultProps.offer.name,
      })
    ).toBeInTheDocument()
  })
})
