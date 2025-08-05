import {
  CollectiveBookingCancellationReasons,
  CollectiveOfferDisplayedStatus,
} from 'apiClient/v1'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from 'commons/core/FirebaseEvents/constants'
import * as duplicateBookableOffer from 'commons/core/OfferEducational/utils/duplicateBookableOffer'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CancelledBanner } from './CancelledBanner'

describe('CancelledBanner', () => {
  const mockLogEvent = vi.fn()
  const mockDuplicateBookableOffer = vi.fn().mockResolvedValue(undefined)
  const cancelledBySchoolMessage =
    'L’établissement scolaire a annulé la réservation.'
  const cancelledByPassCultureMessage =
    'Le pass Culture a annulé votre offre. Vous avez été notifié par mail de la raison de votre annulation. Vous pouvez la dupliquer si vous souhaitez la publier à nouveau.'
  const cancelledByOffererMessage =
    'Vous avez annulé l’offre. Vous pouvez la dupliquer si vous souhaitez la publier à nouveau.'
  const cancelledByExpiredMessage =
    'La date d’évènement de votre offre est dépassée. Votre offre a automatiquement été annulée. Vous pouvez créer une nouvelle offre à partir de celle-ci.'
  const messagePerReason = {
    [CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE]:
      cancelledBySchoolMessage,
    [CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER]:
      cancelledBySchoolMessage,
    [CollectiveBookingCancellationReasons.EXPIRED]: cancelledByExpiredMessage,
    [CollectiveBookingCancellationReasons.OFFERER]: cancelledByOffererMessage,
    [CollectiveBookingCancellationReasons.PUBLIC_API]:
      cancelledByOffererMessage,
    [CollectiveBookingCancellationReasons.BENEFICIARY]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.FRAUD]: cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.FRAUD_SUSPICION]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.FRAUD_INAPPROPRIATE]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.FINANCE_INCIDENT]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.BACKOFFICE]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.BACKOFFICE_EVENT_CANCELLED]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_MODIFIED]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_WITH_WRONG_INFORMATION]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.BACKOFFICE_OFFERER_BUSINESS_CLOSED]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.OFFERER_CONNECT_AS]:
      cancelledByPassCultureMessage,
    [CollectiveBookingCancellationReasons.OFFERER_CLOSED]:
      cancelledByPassCultureMessage,
  } satisfies Record<CollectiveBookingCancellationReasons, string>

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))

    vi.spyOn(
      duplicateBookableOffer,
      'duplicateBookableOffer'
    ).mockImplementation(mockDuplicateBookableOffer)
  })

  it.each(
    Object.keys(messagePerReason) as CollectiveBookingCancellationReasons[]
  )('should display the correct message for reason %s', (reason) => {
    renderWithProviders(<CancelledBanner offerId={2} reason={reason} />)
    expect(screen.getByText(messagePerReason[reason])).toBeInTheDocument()
  })

  it('should display the correct message when no reason are provided', () => {
    renderWithProviders(<CancelledBanner offerId={2} />)
    expect(screen.getByText(cancelledByExpiredMessage)).toBeInTheDocument()
  })

  it('should log event on press Dupliquer', async () => {
    renderWithProviders(<CancelledBanner offerId={2} />)

    const duplicateButton = screen.getByText("Dupliquer l'offre")
    await userEvent.click(duplicateButton)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_BOOKABLE_OFFER,
      {
        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_TIMELINE,
        offerId: 2,
        offerType: 'collective',
        offerStatus: CollectiveOfferDisplayedStatus.CANCELLED,
      }
    )
  })

  it('should duplicate offer on press Dupliquer', async () => {
    renderWithProviders(<CancelledBanner offerId={2} />)

    const duplicateButton = screen.getByText("Dupliquer l'offre")
    await userEvent.click(duplicateButton)

    expect(mockDuplicateBookableOffer).toHaveBeenCalledTimes(1)
  })
})
