import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { CollectiveOfferTemplateAllowedAction } from '@/apiClient/v1'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
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

const renderCollectiveOfferPreviewCreation = (
  path: string,
  props: MandatoryCollectiveOfferFromParamsProps,
  features?: string[]
) => {
  renderWithProviders(<CollectiveOfferPreviewEdition {...props} />, {
    features,
    initialRouterEntries: [path],
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

  it('should not render share link drawer when offer is bookable', async () => {
    renderCollectiveOfferPreviewCreation('/offre/1/collectif/apercu', {
      offerer: undefined,
      isTemplate: false,
      offer: getCollectiveOfferFactory(),
    })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByRole('button', {
        name: 'Partager l’offre',
      })
    ).not.toBeInTheDocument()
  })

  it('should render share link drawer when offer is template', async () => {
    renderCollectiveOfferPreviewCreation('/offre/T-A1/collectif/apercu', {
      ...defaultProps,
      offer: {
        ...defaultProps.offer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_SHARE],
      },
    })

    const shareLinkButton = screen.getByRole('button', {
      name: 'Partager l’offre',
    })

    expect(shareLinkButton).toBeInTheDocument()

    await userEvent.click(shareLinkButton)
    expect(
      await screen.findByText(
        'Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE'
      )
    ).toBeInTheDocument()
  })
})
