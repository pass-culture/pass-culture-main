import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Row } from 'react-table'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { collectiveBookingRecapFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import DetailsButtonCell from '../DetailsButtonCell'

const renderDetailsButtonCell = (row: Row<CollectiveBookingResponseModel>) => {
  renderWithProviders(<DetailsButtonCell bookingRow={row} />)
}

describe('DetailsButtonCell', () => {
  it('should log event when clicking on the button', async () => {
    const mockLogEvent = vi.fn()
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
    const row = {
      original: collectiveBookingRecapFactory(),
    } as Row<CollectiveBookingResponseModel>

    renderDetailsButtonCell(row)

    const detailsButton = screen.getByRole('button', { name: 'Détails' })
    await userEvent.click(detailsButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      CollectiveBookingsEvents.CLICKED_DETAILS_BUTTON_CELL,
      {
        from: '/',
      }
    )
  })
})
