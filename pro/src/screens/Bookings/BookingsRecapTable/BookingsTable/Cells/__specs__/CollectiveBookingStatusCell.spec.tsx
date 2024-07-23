import { screen } from '@testing-library/react'

import { collectiveBookingFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

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
