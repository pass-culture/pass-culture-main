import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { BOOKING_STATUS } from 'core/Bookings'
import { configureTestStore } from 'store/testUtils'
import { collectiveBookingRecapFactory } from 'utils/collectiveApiFactories'

import CollectiveTimeLine from '../CollectiveTimeLine'

const renderCollectiveTimeLine = (
  bookingRecap: CollectiveBookingResponseModel
) => {
  render(
    <Provider store={configureTestStore()}>
      <Router history={createMemoryHistory()}>
        <CollectiveTimeLine bookingRecap={bookingRecap} />
      </Router>
    </Provider>
  )
}

describe('collective timeline', () => {
  it('should render steps for pending booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(
      screen.getByText('Préreservée par l’établissement scolaire')
    ).toBeInTheDocument()
  })
  it('should render steps for booked booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.BOOKED,
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(
      screen.getByText('Réservée par l’établissement scolaire')
    ).toBeInTheDocument()
  })
  it('should render steps for confirmed booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CONFIRMED,
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(screen.getByText('Réservation confirmée')).toBeInTheDocument()
  })
  it('should render steps for validated booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.VALIDATED,
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(
      screen.getByText('Jour J : réservation terminée')
    ).toBeInTheDocument()
  })
  it('should render steps for reimbursed booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.REIMBURSED,
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(screen.getByText('Remboursement effectué')).toBeInTheDocument()
  })
  it('should render steps for cancelled booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CANCELLED,
      bookingStatusHistory: [
        { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
        { date: new Date().toISOString(), status: BOOKING_STATUS.CANCELLED },
      ],
    })
    renderCollectiveTimeLine(bookingRecap)
    expect(
      screen.getByText('Vous avez annulé la réservation')
    ).toBeInTheDocument()
  })
})
