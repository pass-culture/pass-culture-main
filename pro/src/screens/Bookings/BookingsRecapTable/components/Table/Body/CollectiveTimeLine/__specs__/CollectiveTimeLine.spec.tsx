import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
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
  defaultCollectiveBookingStock,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveTimeLine from '../CollectiveTimeLine'

const renderCollectiveTimeLine = (
  bookingRecap: CollectiveBookingResponseModel,
  bookingDetails: CollectiveBookingByIdResponseModel,
  storeOverrides = {}
) =>
  renderWithProviders(
    <CollectiveTimeLine
      bookingRecap={bookingRecap}
      bookingDetails={bookingDetails}
    />,
    {
      storeOverrides,
    }
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
      bookingStatusHistory: [
        { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
        { date: new Date().toISOString(), status: BOOKING_STATUS.CONFIRMED },
        { date: '2023-03-25', status: BOOKING_STATUS.REIMBURSED },
      ],
    })
    renderCollectiveTimeLine(bookingRecap, bookingDetails)
    expect(screen.getByText('Remboursement effectué')).toBeInTheDocument()
    expect(screen.getByText('25 mars 2023')).toBeInTheDocument()
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

    it('should display special message for pending booking if clg 6e 5e ff is active', () => {
      const storeOverrides = {
        features: {
          list: [
            { isActive: true, nameKey: 'WIP_ADD_CLG_6_5_COLLECTIVE_OFFER' },
          ],
        },
      }
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.PENDING,
        stock: {
          bookingLimitDatetime: new Date().toISOString(),
          eventBeginningDatetime: addDays(new Date(), -1).toISOString(),
          numberOfTickets: 1,
          offerIdentifier: '1',
          offerId: 1,
          offerIsEducational: true,
          offerIsbn: null,
          offerName: 'ma super offre collective',
        },
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails, storeOverrides)

      expect(
        screen.getByText(
          /Si votre offre concerne les classes de 6eme et 5eme, le chef d'établissement pourra confirmer la réservation/
        )
      )
    })
  })

  describe('confirmed booking', () => {
    it('should render steps for confirmed booking when event is not passed yet', () => {
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.CONFIRMED,
        stock: {
          ...defaultCollectiveBookingStock,
          eventBeginningDatetime: addDays(new Date(), 1).toISOString(),
        },
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails)
      expect(
        screen.getByText(
          'La réservation n’est plus annulable par l’établissement scolaire. Cependant, vous pouvez encore modifier le prix et le nombre de participants si nécessaire.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Modifier le prix ou le nombre d’élèves',
        })
      ).toBeInTheDocument()
    })
    it('should render steps for confirmed booking when event is passed', () => {
      const bookingRecap = collectiveBookingRecapFactory({
        bookingStatus: BOOKING_STATUS.CONFIRMED,
        stock: {
          ...defaultCollectiveBookingStock,
          eventBeginningDatetime: addDays(new Date(), -2).toISOString(),
        },
      })
      renderCollectiveTimeLine(bookingRecap, bookingDetails)
      expect(
        screen.getByRole('link', {
          name: 'Modifier le prix ou le nombre d’élèves',
        })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Je rencontre un problème à cette étape',
        })
      ).toBeInTheDocument()
    })
  })
})
