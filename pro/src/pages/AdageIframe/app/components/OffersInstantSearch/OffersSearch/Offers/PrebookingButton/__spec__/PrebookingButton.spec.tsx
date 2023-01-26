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
  let stock: {
    id: number
    beginningDatetime: string | number | null | undefined
    bookingLimitDatetime: string | number | null | undefined
    isBookable: boolean
    price: number
    numberOfTickets: number | null | undefined
    educationalPriceDetail: string | number | null | undefined
  }
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
      render(
        <PrebookingButton
          canPrebookOffers={false}
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.queryByText('Préréserver')).not.toBeInTheDocument()
    })

    it('should display when prebooking is activated', async () => {
      // Given
      render(
        <PrebookingButton
          canPrebookOffers
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.getByText('Préréserver')).toBeInTheDocument()
    })
  })
})
