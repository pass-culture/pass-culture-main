import { screen } from '@testing-library/react'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { COLLECTIVE_OFFER_CREATION_TITLE } from '@/components/CollectiveBudgetInformation/constants'

import {
  CollectiveOfferLayout,
  type CollectiveOfferLayoutProps,
} from '../CollectiveOfferLayout'

const renderCollectiveOfferLayout = (
  path: string,
  props: Partial<CollectiveOfferLayoutProps>
) => {
  renderWithProviders(
    <CollectiveOfferLayout subTitle="Ma super offre" {...props}>
      Test
    </CollectiveOfferLayout>,
    {
      initialRouterEntries: [path],

      storeOverrides: {
        offerer: {
          currentOfferer: { allowedOnAdage: true },
        },
      },
    }
  )
}

describe('CollectiveOfferLayout', () => {
  it('should render edition title page', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/edition', {})
    expect(screen.getByText('Modifier l’offre')).toBeInTheDocument()
  })

  it('should render subtitle if provided', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/edition', {})

    const offersubTitle = screen.getByText('Ma super offre')
    const tagOfferTemplate = screen.queryByText('Offre vitrine')

    expect(offersubTitle).toBeInTheDocument()
    expect(tagOfferTemplate).not.toBeInTheDocument()
  })

  it("should render 'Offre vitrine' tag if offer is template", () => {
    renderCollectiveOfferLayout('/offre/T-A1/collectif/edition', {
      isTemplate: true,
    })

    const tagOfferTemplate = screen.getByText('Offre vitrine')

    expect(tagOfferTemplate).toBeInTheDocument()
  })

  it('should render summary page layout in edition', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/recapitulatif', {})

    const title = screen.getByRole('heading', { name: /Récapitulatif/ })

    expect(title).toBeInTheDocument()
  })

  it('should display creation title', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', { isCreation: true })

    const title = screen.getByRole('heading', {
      name: /Créer une offre/,
    })

    expect(title).toBeInTheDocument()
  })

  it('should display creation from template title', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', {
      isCreation: true,
    })

    const title = screen.getByRole('heading', {
      name: /Créer une offre réservable/,
    })

    expect(title).toBeInTheDocument()
  })

  it('should render budget information callout when creating offer', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', {
      isCreation: true,
    })

    expect(
      screen.getByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).toBeInTheDocument()
  })

  it('should not render budget information callout when reading offer', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', {
      isCreation: false,
    })

    expect(
      screen.queryByText(COLLECTIVE_OFFER_CREATION_TITLE)
    ).not.toBeInTheDocument()
  })
})
