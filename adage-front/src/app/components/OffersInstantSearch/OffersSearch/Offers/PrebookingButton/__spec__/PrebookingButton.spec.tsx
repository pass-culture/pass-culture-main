import { render, screen } from '@testing-library/react'
import React from 'react'

import PrebookingButton from '../PrebookingButton'

jest.mock('repository/pcapi/pcapi', () => ({
  preBookStock: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: { bookCollectiveOffer: jest.fn() },
}))

describe('offer', () => {
  let stock
  beforeEach(() => {
    stock = {
      id: 117,
      beginningDatetime: Date.now(),
      bookingLimitDatetime: Date.now(),
      isBookable: true,
      price: 20,
      numberOfTickets: 3,
      educationalPriceDetail: 1200,
    }
  })

  describe('offer item', () => {
    it('should not display when prebooking is not activated', async () => {
      // Given
      render(<PrebookingButton canPrebookOffers={false} stock={stock} />)
      // When - Then
      expect(screen.queryByText('Préréserver')).not.toBeInTheDocument()
    })

    it('should display when prebooking is activated', async () => {
      // Given
      render(<PrebookingButton canPrebookOffers stock={stock} />)
      // When - Then
      expect(screen.getByText('Préréserver')).toBeInTheDocument()
    })
  })
})
