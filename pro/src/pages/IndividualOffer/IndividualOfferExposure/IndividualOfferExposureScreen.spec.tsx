import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  MOCKED_CATEGORIES,
  MOCKED_SUBCATEGORIES,
} from '../commons/__mocks__/constants'
import { IndividualOfferExposureScreen } from './IndividualOfferExposureScreen'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOfferExposure: vi.fn(),
  },
}))

const renderIndividualOfferLocationScreen = ({
  offer,
}: {
  offer: GetIndividualOfferResponseModelV2
}) => {
  const contextValues: IndividualOfferContextValues = {
    categories: MOCKED_CATEGORIES,
    hasPublishedOfferWithSameEan: false,
    isEvent: null,
    setIsControlledEvent: vi.fn(),
    subCategories: MOCKED_SUBCATEGORIES,
    offer,
    offerId: offer.id,
  }
  const selectedPartnerVenue = makeGetVenueResponseModel({
    id: 1,
  })
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue,
      },
    },
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <IndividualOfferExposureScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('IndividualOfferExposureScreen', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferExposure').mockResolvedValue({
      views: 0,
      events: [],
    })
  })

  it('should render and pass accessibility checks', async () => {
    const offer = getIndividualOfferFactory({ bookingsCount: 42 })
    const { container } = renderIndividualOfferLocationScreen({ offer })

    expect(
      await screen.findByRole('heading', { name: 'Actions de mise en avant' })
    ).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the component', async () => {
    const offer = getIndividualOfferFactory({ bookingsCount: 42 })
    renderIndividualOfferLocationScreen({ offer })

    expect(
      await screen.findByRole('heading', { name: 'Actions de mise en avant' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        name: 'Statistiques de votre offre',
      })
    ).toBeInTheDocument()
    expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
  })
})
