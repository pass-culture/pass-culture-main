import { screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { BookingWaitingBanner } from './BookingWaitingBanner'

describe('BookingWaitingBanner', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should show expiration warning when offer expires within 7 days', () => {
    const inThreeDays = new Date()
    inThreeDays.setDate(inThreeDays.getDate() + 3)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        bookingLimitDatetime={inThreeDays.toISOString()}
      />
    )

    expect(screen.getByText(/expire dans 3 jours/)).toBeInTheDocument()

    const callout = screen.getByTestId('callout-booking-waiting')
    expect(callout.className).toMatch(/warning/)
  })

  it('should show "expire aujourd’hui" when offer expires today', () => {
    const today = new Date()

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        bookingLimitDatetime={today.toISOString()}
      />
    )

    expect(screen.getByText(/expire aujourd’hui/)).toBeInTheDocument()
  })

  it('should not show expiration warning when offer expires in more than 7 days', () => {
    const inTenDays = new Date()
    inTenDays.setDate(inTenDays.getDate() + 10)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        bookingLimitDatetime={inTenDays.toISOString()}
      />
    )

    expect(screen.queryByText(/expire/)).not.toBeInTheDocument()

    const callout = screen.getByTestId('callout-booking-waiting')
    expect(callout.className).toMatch(/info/)
  })

  it('should show a mailto link when contact email is provided and offer expires soon', () => {
    const inThreeDays = new Date()
    inThreeDays.setDate(inThreeDays.getDate() + 3)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
        bookingLimitDatetime={inThreeDays.toISOString()}
        contactEmail="contact@etablissement.fr"
      />
    )

    expect(
      screen.getByRole('link', { name: /Contacter l'établissement/ })
    ).toHaveAttribute('href', 'mailto:contact@etablissement.fr')
  })

  it('should not show a mailto link when contact email is provided and offer expires in more than 7 days', () => {
    const inTenDays = new Date()
    inTenDays.setDate(inTenDays.getDate() + 10)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
        bookingLimitDatetime={inTenDays.toISOString()}
        contactEmail="contact@etablissement.fr"
      />
    )

    expect(
      screen.queryByRole('link', { name: /Contacter l'établissement/ })
    ).not.toBeInTheDocument()
  })

  it('should show teacher prebook action warning when offer is published', () => {
    const inTenDays = new Date()
    inTenDays.setDate(inTenDays.getDate() + 10)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        bookingLimitDatetime={inTenDays.toISOString()}
      />
    )

    expect(
      screen.getByText(
        /L'enseignant doit impérativement préréserver l'offre avant le/
      )
    ).toBeInTheDocument()
  })

  it('should show head of school book action warning when offer is prebooked', () => {
    const inTenDays = new Date()
    inTenDays.setDate(inTenDays.getDate() + 10)

    renderWithProviders(
      <BookingWaitingBanner
        offerId={123}
        offerStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
        bookingLimitDatetime={inTenDays.toISOString()}
      />
    )

    expect(
      screen.getByText(
        /Le chef d'établissement doit impérativement confirmer la préréservation de l'offre avant le/
      )
    ).toBeInTheDocument()
  })
})
