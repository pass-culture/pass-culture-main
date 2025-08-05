import { api } from 'apiClient/api'
import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import {
  defaultGetVenue,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { MandatoryCollectiveOfferFromParamsProps } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

import { CollectiveOfferPreviewEdition } from '../CollectiveOfferPreviewEdition'

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useParams: () => ({
    requestId: vi.fn(),
    requete: '1',
  }),
  useNavigate: vi.fn(),
  default: vi.fn(),
}))

vi.mock('apiClient/api', () => ({
  api: {
    getVenue: vi.fn(),
  },
}))

const renderCollectiveOfferPreviewCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferPreviewEdition {...props} />, {
    ...options,
    initialRouterEntries: [path],
  })
}

const defaultProps = {
  offer: getCollectiveOfferTemplateFactory(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferPreviewCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)
  })

  it('should render collective offer preview edition', async () => {
    renderCollectiveOfferPreviewCreation(
      '/offre/T-A1/collectif/apercu',
      defaultProps
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: 'Aperçu de l’offre',
      })
    ).toBeInTheDocument()
  })
})
