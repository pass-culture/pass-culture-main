import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { buildCollectiveStock } from '@/commons/utils/factories/adageFactories'

import { CollectiveOffersBookableTag } from './CollectiveOffersBookableTag'

describe('<CollectiveOffersBookableTag />', () => {
  it('should render without accessibility violations', async () => {
    const stock = buildCollectiveStock(1, 2)
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
      const stock = buildCollectiveStock(1, 2)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PUBLISHED}
          stock={stock}
        />
      )

      expect(screen.getByText('Expire dans 1 jour')).toBeVisible()
    })

    it('should pluralize the label when there are several days', () => {
      const stock = buildCollectiveStock(7, 8)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText('Expire dans 7 jours')).toBeVisible()
    })

    it('should display "Expire aujourd\'hui" if it is the case', () => {
      const stock = buildCollectiveStock(0, 1)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.PREBOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText("Expire aujourd'hui")).toBeVisible()
    })

    it('should show the days from start for the other offers', () => {
      const stock = buildCollectiveStock(8, 9)
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
      const stock = buildCollectiveStock(0, 1)
      render(
        <CollectiveOffersBookableTag
          displayedStatus={CollectiveOfferDisplayedStatus.BOOKED}
          stock={stock}
        />
      )

      expect(screen.getByText('Dans 1 jour')).toBeVisible()
    })

    it('should display "Aujourd\'hui" if the start date si today', () => {
      const stock = buildCollectiveStock(0, 0)
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
