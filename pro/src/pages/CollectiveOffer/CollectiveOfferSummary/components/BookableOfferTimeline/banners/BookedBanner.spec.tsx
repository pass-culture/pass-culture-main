import { screen } from '@testing-library/react'
import { addDays, format, subDays } from 'date-fns'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { BookedBanner } from './BookedBanner'

describe('BookedBanner', () => {
  const baseProps = {
    offerId: 123,
    departmentCode: '75',
  }

  it('should display the "not cancellable anymore" message if cancellationLimitDate is in the past', () => {
    const cancellationLimitDate = subDays(new Date(), 1).toISOString()
    renderWithProviders(
      <BookedBanner
        {...baseProps}
        cancellationLimitDate={cancellationLimitDate}
        canEditDiscount={true}
      />
    )
    expect(
      screen.getByText(
        /La réservation n’est plus annulable par l’établissement scolaire/i
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /vous pouvez annuler la réservation ou modifier à la baisse le prix ou le nombre de participants jusqu’à 48 heures après la date de l’évènement/i
      )
    ).toBeInTheDocument()
  })

  it('should display the "confirmed" message with the formatted date when cancellationLimitDate is in the future', () => {
    const cancellationLimitDate = addDays(new Date(), 1).toISOString()
    const formattedDate = format(new Date(cancellationLimitDate), 'dd/MM/yyyy')

    renderWithProviders(
      <BookedBanner
        {...baseProps}
        cancellationLimitDate={cancellationLimitDate}
        canEditDiscount={true}
      />
    )
    expect(
      screen.getByText(
        /Le chef d’établissement a confirmé la préréservation de l’offre/i
      )
    ).toBeInTheDocument()
    expect(screen.getByText(new RegExp(formattedDate))).toBeInTheDocument()
    expect(
      screen.getByText(
        /la réservation ne sera plus annulable par l’établissement scolaire/i
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /vous pouvez annuler la réservation et modifier le prix ou le nombre d’élève à la baisse jusqu’à 48 heures après la date de l’évènement/i
      )
    ).toBeInTheDocument()
  })

  it('should display the edit link if canEditDiscount is true', () => {
    const cancellationLimitDate = new Date().toISOString()
    renderWithProviders(
      <BookedBanner
        {...baseProps}
        cancellationLimitDate={cancellationLimitDate}
        canEditDiscount={true}
      />
    )
    expect(
      screen.getByRole('link', {
        name: /Modifier à la baisse le prix ou le nombre d’élèves/i,
      })
    ).toHaveAttribute('href', '/offre/123/collectif/stocks/edition')
  })

  it('should not display the edit link if canEditDiscount is false', () => {
    const cancellationLimitDate = new Date().toISOString()
    renderWithProviders(
      <BookedBanner
        {...baseProps}
        cancellationLimitDate={cancellationLimitDate}
        canEditDiscount={false}
      />
    )
    expect(
      screen.queryByRole('link', {
        name: /Modifier à la baisse le prix ou le nombre d’élèves/i,
      })
    ).not.toBeInTheDocument()
  })

  it('should render nothing if cancellationLimitDate is undefined', () => {
    renderWithProviders(
      <BookedBanner
        offerId={123}
        departmentCode="75"
        cancellationLimitDate={undefined}
        canEditDiscount={true}
      />
    )
    expect(
      screen.queryByText(
        /Le chef d’établissement a confirmé la préréservation de l’offre/i
      )
    ).not.toBeInTheDocument()
  })
})
