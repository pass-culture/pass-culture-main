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

import { Component as IndividualOfferDescription } from './IndividualOfferDescription'

vi.mock('./components/IndividualOfferDescriptionScreen', () => ({
  IndividualOfferDescriptionScreen: () => (
    <div data-testid="description-screen" />
  ),
}))

const renderIndividualOfferDescription = (
  contextValues: Partial<IndividualOfferContextValues> = {}
) => {
  const contextValue: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...contextValues,
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <IndividualOfferDescription />
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

describe('<IndividualOfferDescription />', () => {
  it('should render the description screen within the offer layout', () => {
    renderIndividualOfferDescription({ offer: getIndividualOfferFactory() })

    expect(screen.getByTestId('description-screen')).toBeInTheDocument()
  })
})
