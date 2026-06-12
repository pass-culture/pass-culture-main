import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

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

const renderIndividualOfferLocationScreen = () => {
  const offer = getIndividualOfferFactory()
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
  it('should render and pass accessibility checks', async () => {
    const { container } = renderIndividualOfferLocationScreen()

    expect(
      await screen.findByRole('heading', { name: 'Actions de mise en avant' })
    ).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the component', async () => {
    renderIndividualOfferLocationScreen()

    expect(
      await screen.findByRole('heading', { name: 'Actions de mise en avant' })
    ).toBeInTheDocument()
    expect(screen.getByText('Visualiser dans l’app')).toBeInTheDocument()
  })
})
