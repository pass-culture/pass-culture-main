import { screen } from '@testing-library/react'

import { collectiveBookingFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveBookingStatusCell,
  CollectiveBookingStatusCellProps,
} from '../CollectiveBookingStatusCell'

const renderCollectiveBookingStatusCell = (
  props: CollectiveBookingStatusCellProps
) => renderWithProviders(<CollectiveBookingStatusCell {...props} />)

describe('CollectiveBookingStatusCell', () => {
  it('should display the status label', () => {
    renderCollectiveBookingStatusCell({
      booking: collectiveBookingFactory(),
    })

    expect(screen.getByText('préréservée')).toBeInTheDocument()
  })
})
