import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { MandatoryCollectiveOfferFromParamsProps } from 'screens/OfferEducational/useCollectiveOfferFromParams'
import { defaultAdageUser } from 'utils/adageFactories'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { CollectiveOfferPreviewCreation } from '../CollectiveOfferPreviewCreation'

vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    requestId: vi.fn(),
    requete: '1',
  }),
  useNavigate: () => vi.fn(),
  default: vi.fn(),
}))

const renderCollectiveOfferPreviewCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <CollectiveOfferPreviewCreation {...props} />
    </AdageUserContextProvider>,
    {
      ...options,
      initialRouterEntries: [path],
    }
  )
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

  it('should show the redirect modal', async () => {
    vi.spyOn(api, 'patchCollectiveOfferPublication').mockResolvedValue({
      ...getCollectiveOfferFactory(),
      isNonFreeOffer: true,
    })

    renderCollectiveOfferPreviewCreation(
      '/offre/A1/collectif/creation/apercu',
      {
        ...defaultProps,
        offer: getCollectiveOfferFactory(),
        offerer: {
          ...defaultGetOffererResponseModel,
          hasNonFreeOffer: false,
          hasValidBankAccount: false,
        },
      }
    )

    await userEvent.click(screen.getByText('Publier l’offre'))

    screen.getByText(/Félicitations, vous avez créé votre offre !/)
  })
})
