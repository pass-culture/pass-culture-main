import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import {
  defaultGetVenue,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import type { MandatoryCollectiveOfferFromParamsProps } from '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

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

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenue: vi.fn(),
  },
}))

const renderCollectiveOfferPreviewEdition = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  features?: string[]
) => {
  renderWithProviders(<CollectiveOfferPreviewEdition {...props} />, {
    features,
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
      },
    },
  })
}

const defaultProps = {
  offer: getCollectiveOfferTemplateFactory({ isTemplate: true }),
  isTemplate: true,
  offerer: undefined,
}

describe('CollectiveOfferPreviewCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)
  })

  it('should render collective offer preview edition', async () => {
    renderCollectiveOfferPreviewEdition(
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
