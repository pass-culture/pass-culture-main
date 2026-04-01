import { render, screen } from '@testing-library/react'
import { addDays } from 'date-fns'
import { axe } from 'vitest-axe'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'

import type { CollectiveOffersBookableCTA } from '../CollectiveOffersBookableCTA/CollectiveOffersBookableCTA'
import { CollectiveOffersBookableTag } from './CollectiveOffersBookableTag'

function getStock(
  bookingDateDaysFromToday: number,
  startDateDaysFromToday: number
): NonNullable<
  React.ComponentProps<typeof CollectiveOffersBookableCTA>['stock']
> {
  const today = new Date()
  return {
    bookingLimitDatetime: addDays(
      today,
      bookingDateDaysFromToday
    ).toISOString(),
    startDatetime: addDays(today, startDateDaysFromToday).toISOString(),
    endDatetime: addDays(today, startDateDaysFromToday + 1).toISOString(),
    numberOfTickets: 100,
  }
}

describe('<CollectiveOffersBookableTag />', () => {
  it('should render without accessibility violations', async () => {
    const stock = getStock(1, 2)
    const { container } = render(
      <CollectiveOffersBookableTag
        displayedStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
        stock={stock}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  describe('for expirable offers (PREBOOKED and PUBLISHED displayedStatuses)', () => {
    it('should show the days before expiration for offers that expire in less than 7 days', () => {
      const stock = getStock(1, 2)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
          stock={stock}
        />
      )

      expect(screen.getByText('Expire dans 1 jour')).toBeVisible()
    })

    it('should pluralize the label when there are several days', () => {
      const stock = getStock(7, 8)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText('Expire dans 7 jours')).toBeVisible()
    })

    it('should display "Expire aujourd\'hui" if it is the case', () => {
      const stock = getStock(0, 1)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText("Expire aujourd'hui")).toBeVisible()
    })

    it('should show the days from start for the other offers', () => {
      const stock = getStock(8, 9)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
          stock={stock}
        />
      )

      expect(screen.getByText('Dans 9 jours')).toBeVisible()
    })
  })

  describe('for non expirable offers (the other displayedStatuses)', () => {
    it('should show the days from start for the other offers', () => {
      const stock = getStock(0, 1)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.BOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText('Dans 1 jour')).toBeVisible()
    })

    it('should display "Aujourd\'hui" if the start date si today', () => {
      const stock = getStock(0, 0)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.BOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText("Aujourd'hui")).toBeVisible()
    })
  })
})
