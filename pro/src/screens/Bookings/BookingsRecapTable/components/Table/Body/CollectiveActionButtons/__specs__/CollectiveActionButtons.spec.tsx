import { screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import React from 'react'

import { BOOKING_STATUS } from 'core/Bookings'
import {
  collectiveBookingRecapFactory,
  defaultCollectiveBookingStock,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveActionButtons from '..'
import { ICollectiveActionButtonsProps } from '../CollectiveActionButtons'

const renderCollectiveActionButtons = (
  props: ICollectiveActionButtonsProps
) => {
  renderWithProviders(<CollectiveActionButtons {...props} />)
}

describe('CollectiveActionButtons', () => {
  it('should display modify offer button for validated booking for less than 2 days', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: {
        ...defaultCollectiveBookingStock,
        eventBeginningDatetime: addDays(new Date(), 2).toISOString(),
      },
    })
    renderCollectiveActionButtons({
      bookingRecap,
      reloadBookings: jest.fn(),
      isCancellable: false,
    })
    const modifyLink = screen.getByRole('link', { name: 'Modifier l’offre' })
    expect(modifyLink).toBeInTheDocument()
    expect(modifyLink).toHaveAttribute(
      'href',
      '/offre/1/collectif/stocks/edition'
    )
  })
  it('should display modify offer button for pending booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
    })
    renderCollectiveActionButtons({
      bookingRecap,
      reloadBookings: jest.fn(),
      isCancellable: false,
    })
    const modifyLink = screen.getByRole('link', { name: 'Modifier l’offre' })
    expect(modifyLink).toBeInTheDocument()
    expect(modifyLink).toHaveAttribute(
      'href',
      '/offre/1/collectif/recapitulatif'
    )
  })
  it('should not display modify offer button for validated booking for more than 2 days', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
      stock: {
        ...defaultCollectiveBookingStock,
        eventBeginningDatetime: addDays(new Date(), 3).toISOString(),
      },
    })
    renderCollectiveActionButtons({
      bookingRecap,
      reloadBookings: jest.fn(),
      isCancellable: false,
    })
    expect(
      screen.queryByRole('link', { name: 'Modifier l’offre' })
    ).not.toBeInTheDocument()
  })
})
