import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { defaultAdageUser } from 'commons/utils/factories/adageFactories'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { MandatoryCollectiveOfferFromParamsProps } from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'

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

const mockLogEvent = vi.fn()

describe('CollectiveOfferPreviewCreation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should render collective offer preview ', async () => {
    renderCollectiveOfferPreviewCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )
    expect(
      screen.getByRole('heading', {
        name: /Créer une offre/,
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

  it('should call tracker when clicking save draft and exit', async () => {
    renderCollectiveOfferPreviewCreation(
      '/offre/A1/collectif/creation/recapitulatif',
      defaultProps
    )

    await userEvent.click(
      await screen.findByRole('link', {
        name: /Sauvegarder le brouillon et quitter/,
      })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER,
      {
        from: '/',
        offerId: defaultProps.offer.id,
        offerType: 'collective',
      }
    )
  })
})
