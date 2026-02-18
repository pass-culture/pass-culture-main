import { screen } from '@testing-library/react'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ExpiredBanner } from './ExpiredBanner'

describe('ExpiredBanner', () => {
  const baseProps = {
    offerId: 42,
    bookingLimitDatetime: '2025-08-31T12:00:00Z',
    departmentCode: '75',
  }

  it('should display the teacher message if the status before expired status is PUBLISHED', () => {
    renderWithProviders(
      <ExpiredBanner
        {...baseProps}
        stepBeforeExpiredStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        canEditDates
      />
    )
    expect(
      screen.getByText(/L’enseignant n’a pas préréservé l’offre/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Pour qu’il puisse préréserver à nouveau, vous pouvez modifier la date limite de réservation, ce qui rendra automatiquement la préréservation disponible auprès de l’enseignant.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: /Modifier la date limite de réservation/i,
      })
    ).toHaveAttribute('href', '/offre/42/collectif/stocks/edition')
    expect(screen.getByText(/31\/08\/2025/)).toBeInTheDocument()
  })

  it('should display the principal message if the status before expired status is PREBOOKED', () => {
    renderWithProviders(
      <ExpiredBanner
        {...baseProps}
        stepBeforeExpiredStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
        canEditDates
      />
    )
    expect(
      screen.getByText(/Le chef d’établissement n’a pas réservé l’offre/i)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Pour qu’il puisse réserver à nouveau, vous pouvez modifier la date limite de réservation, ce qui rendra automatiquement la réservation disponible auprès de l’enseignant.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', {
        name: /Modifier la date limite de réservation/i,
      })
    ).toHaveAttribute('href', '/offre/42/collectif/stocks/edition')
    expect(screen.getByText(/31\/08\/2025/)).toBeInTheDocument()
  })

  it('should not show edit dates link if canEditDates is false', () => {
    renderWithProviders(
      <ExpiredBanner
        offerId={42}
        bookingLimitDatetime="2025-08-31T12:00:00Z"
        departmentCode="75"
        stepBeforeExpiredStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        canEditDates={false}
      />
    )
    expect(
      screen.queryByRole('link', {
        name: /Modifier la date limite de réservation/i,
      })
    ).toBeFalsy()
  })
})
