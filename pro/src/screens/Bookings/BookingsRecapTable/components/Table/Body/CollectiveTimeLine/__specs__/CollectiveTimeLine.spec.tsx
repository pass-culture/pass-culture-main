import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import {
  CollectiveBookingBankInformationStatus,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { CollectiveBookingCancellationReasons } from 'apiClient/v1/models/CollectiveBookingCancellationReasons'
import { BOOKING_STATUS } from 'core/Bookings'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  collectiveBookingDetailsFactory,
  collectiveBookingRecapFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveTimeLine from '../CollectiveTimeLine'

const renderCollectiveTimeLine = (
  bookingRecap: CollectiveBookingResponseModel,
  bookingDetails: CollectiveBookingByIdResponseModel
) =>
  renderWithProviders(
    <CollectiveTimeLine
      bookingRecap={bookingRecap}
      bookingDetails={bookingDetails}
    />
  )

describe('collective timeline', () => {
  let bookingDetails = collectiveBookingDetailsFactory()
  it('should render steps for pending booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(
      screen.getByText('Préreservée par l’établissement scolaire')
    ).toBeInTheDocument()
  })
  it('should render steps for booked booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.BOOKED,
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(
      screen.getByText('Réservée par l’établissement scolaire')
    ).toBeInTheDocument()
  })
  it('should render steps for confirmed booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CONFIRMED,
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(screen.getByText('Réservation confirmée')).toBeInTheDocument()
  })

  it('should render steps for reimbursed booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.REIMBURSED,
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(screen.getByText('Remboursement effectué')).toBeInTheDocument()
  })
  it('should render steps for cancelled booking', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CANCELLED,
      bookingConfirmationDate: null,
      bookingCancellationReason: CollectiveBookingCancellationReasons.OFFERER,
      bookingStatusHistory: [
        { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
        { date: new Date().toISOString(), status: BOOKING_STATUS.CANCELLED },
      ],
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(
      screen.getByText('Vous avez annulé la réservation')
    ).toBeInTheDocument()
  })
  it('should render steps for cancelled booking by fraud', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CANCELLED,
      bookingConfirmationDate: null,
      bookingCancellationReason: CollectiveBookingCancellationReasons.FRAUD,
      bookingStatusHistory: [
        { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
        { date: new Date().toISOString(), status: BOOKING_STATUS.CANCELLED },
      ],
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(
      screen.getByText('Le pass Culture a annulé la réservation')
    ).toBeInTheDocument()
  })
  it('should render steps for cancelled booking expired', () => {
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.CANCELLED,
      bookingConfirmationDate: null,
      bookingConfirmationLimitDate: '01/01/2023',
      bookingCancellationReason: CollectiveBookingCancellationReasons.EXPIRED,
      bookingStatusHistory: [
        { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
        { date: new Date().toISOString(), status: BOOKING_STATUS.CANCELLED },
      ],
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(
      screen.getByText(
        /L’établissement scolaire n’a pas confirmé la préréservation avant la date limite de réservation fixée au 01 janvier 2023./
      )
    ).toBeInTheDocument()
  })

  it('should log event when clicking modify booking limit date', async () => {
    const mockLogEvent = jest.fn()
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
    const bookingRecap = collectiveBookingRecapFactory({
      bookingStatus: BOOKING_STATUS.PENDING,
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    const modifyLink = screen.getByRole('link', {
      name: 'Modifier la date limite de réservation',
    })
    await userEvent.click(modifyLink)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      CollectiveBookingsEvents.CLICKED_MODIFY_BOOKING_LIMIT_DATE,
      {
        from: '/',
      }
    )
  })
  describe('validated booking', () => {
    it('should render steps for validated booking and accepted bankInformation', () => {
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.VALIDATED,
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails)
      expect(
        screen.getByText(
          "À compter du jour de l'évènement, le virement sera exécuté dans un délai de 2 à 3 semaines."
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Voir le calendrier des remboursements',
        })
      ).toHaveAttribute(
        'href',
        'https://aide.passculture.app/hc/fr/articles/4411992051601'
      )
    })

    it('should render steps for validated booking and pending bankInformation', () => {
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.VALIDATED,
      })
      bookingDetails = collectiveBookingDetailsFactory({
        bankInformationStatus: CollectiveBookingBankInformationStatus.DRAFT,
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails)
      expect(
        screen.getByText(
          'Les coordonnées bancaires de votre lieu sont en cours de validation par notre service financier. Vos remboursements seront rétroactifs une fois vos coordonnées bancaires ajoutées.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', { name: 'Voir le dossier en cours' })
      ).toHaveAttribute(
        'href',
        'https://www.demarches-simplifiees.fr/dossiers/1/messagerie'
      )
    })

    it('should render steps for validated booking and missing bankInformation', () => {
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.VALIDATED,
      })
      bookingDetails = collectiveBookingDetailsFactory({
        bankInformationStatus: CollectiveBookingBankInformationStatus.MISSING,
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails)
      expect(
        screen.getByText(
          'Vous devez renseigner des coordonnées bancaires pour percevoir le remboursement.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Renseigner mes coordonnées bancaires',
        })
      ).toHaveAttribute(
        'href',
        '/structures/O1/lieux/V1?modification#reimbursement-section'
      )
    })
  })
})
