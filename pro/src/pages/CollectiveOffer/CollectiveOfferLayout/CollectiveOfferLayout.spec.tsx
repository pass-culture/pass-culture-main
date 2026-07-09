import { screen } from '@testing-library/react'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

import type { GetVenueResponseModel } from '@/apiClient/v1'
import { VenueState } from '@/apiClient/v1'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferLayout,
  type CollectiveOfferLayoutProps,
} from './CollectiveOfferLayout'

const renderCollectiveOfferLayout = (
  path: string,
  props: Partial<CollectiveOfferLayoutProps>,
  venueOverrides?: Partial<GetVenueResponseModel>
) => {
  renderWithProviders(
    <CollectiveOfferLayout subTitle="Ma super offre" {...props}>
      Test
    </CollectiveOfferLayout>,
    {
      initialRouterEntries: [path],

      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            allowedOnAdage: true,
            ...venueOverrides,
          }),
        },
      },
    }
  )
}

describe('CollectiveOfferLayout', () => {
  it('should render edition title page', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/edition', {})
    expect(screen.getByText("Modifier l'offre")).toBeInTheDocument()
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

  it('should render the navigation stepper when the partner venue is open', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', { isCreation: true })

    expect(screen.getByTestId('stepper')).toBeVisible()
  })

  it('should not render the navigation stepper when the partner venue is not allowed on Adage', () => {
    renderCollectiveOfferLayout(
      '/offre/A1/collectif/',
      { isCreation: true },
      { allowedOnAdage: false }
    )

    expect(screen.queryByTestId('stepper')).not.toBeInTheDocument()
  })

  it('should not render the navigation stepper when the partner venue is closed', () => {
    renderCollectiveOfferLayout(
      '/offre/A1/collectif/',
      { isCreation: true },
      { state: VenueState.CLOSED }
    )

    expect(screen.queryByTestId('stepper')).not.toBeInTheDocument()
  })
})
