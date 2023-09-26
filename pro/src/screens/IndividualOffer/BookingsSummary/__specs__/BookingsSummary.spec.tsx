import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import {
  IndividualOfferContextValues,
  IndividualOfferContext,
} from 'context/IndividualOfferContext'
import { IndividualOffer } from 'core/Offers/types'
import { bookingRecapFactory } from 'utils/apiFactories'
import {
  individualOfferFactory,
  individualOfferSubCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { BookingsSummaryScreen } from '../BookingsSummary'

const duoSubcategory = individualOfferSubCategoryFactory({ canBeDuo: true })
const render = (offer: IndividualOffer) => {
  const contextValue: IndividualOfferContextValues = {
    offerId: null,
    offer,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [duoSubcategory],
    setOffer: () => {},
    setSubcategory: () => {},
    showVenuePopin: {},
  }

  renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <BookingsSummaryScreen />
    </IndividualOfferContext.Provider>
  )
}

describe('BookingsSummary', () => {
  it('should render a list of bookings', async () => {
    const offer = individualOfferFactory({ name: 'Offre de test' })

    vi.spyOn(api, 'getBookingsPro').mockResolvedValue({
      bookingsRecap: [
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
        bookingRecapFactory({}, offer),
      ],
      page: 1,
      pages: 1,
      total: 3,
    })

    render(offer)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(/Réservations/)).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Offre de test' })).toHaveLength(
      3
    )
  })
})
