import { render } from '@testing-library/react'
import { axe } from 'vitest-axe'

import type {
  CollectiveOffersCardVariant,
  CollectiveOffersVariantMap,
} from '../../../types'
import { CollectiveOffersBookableLine } from './CollectiveOffersBookableLine'

const defaultCollectiveOfferHome = {
  id: 435,
  name: 'Test Matt',
  displayedStatus: 'PUBLISHED',
  imageUrl:
    'http://localhost:5001/storage/thumbs/collectiveoffer/00000004357405842.jpg',
  allowedActions: [
    'CAN_EDIT_DETAILS',
    'CAN_EDIT_DATES',
    'CAN_EDIT_DISCOUNT',
    'CAN_DUPLICATE',
    'CAN_ARCHIVE',
  ],
  collectiveStock: {
    startDatetime: '2026-06-25T22:15:00Z',
    endDatetime: '2026-06-25T22:15:00Z',
    bookingLimitDatetime: '2026-06-25T22:15:00Z',
    numberOfTickets: 1,
  },
} as CollectiveOffersVariantMap[CollectiveOffersCardVariant.BOOKABLE]

describe('<CollectiveOffersBookableLine />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <CollectiveOffersBookableLine offer={defaultCollectiveOfferHome} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })
})
