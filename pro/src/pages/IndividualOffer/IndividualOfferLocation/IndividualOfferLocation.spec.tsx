import { screen } from '@testing-library/react'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { IndividualOfferLocation } from './IndividualOfferLocation'

vi.mock('./components/IndividualOfferLocationScreen', () => ({
  IndividualOfferLocationScreen: () => <div data-testid="location-screen" />,
}))

vi.mock('@/components/IndividualOfferLayout/IndividualOfferLayout', () => ({
  IndividualOfferLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="layout-child">{children}</div>
  ),
}))

const renderIndividualOfferLocation = (
  contextValues: Partial<IndividualOfferContextValues> = {}
) => {
  const contextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...contextValues,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferLocation />
    </IndividualOfferContext.Provider>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )
}

describe('<IndividualOfferLocation />', () => {
  it('should render the spinner when no offer is in context', () => {
    renderIndividualOfferLocation({
      offer: undefined as unknown as IndividualOfferContextValues['offer'],
    })

    expect(screen.getByTestId('spinner')).toBeInTheDocument()
  })

  it('should render the location screen within the offer layout when an offer is provided', () => {
    renderIndividualOfferLocation({ offer: getIndividualOfferFactory() })

    expect(screen.getByTestId('location-screen')).toBeInTheDocument()
  })
})
