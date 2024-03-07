import { screen } from '@testing-library/react'

import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { getCollectiveOfferFactory } from 'utils/collectiveApiFactories'
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
  offer: getCollectiveOfferFactory(),
  setOffer: vi.fn(),
  reloadCollectiveOffer: vi.fn(),
  isTemplate: false,
  offerer: undefined,
}

describe('CollectiveOfferPreviewCreation', () => {
  it('should render collective offer preview ', () => {
    renderCollectiveOfferPreviewCreation(
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
        name: 'aperçu',
      })
    ).toBeInTheDocument()
  })
})
