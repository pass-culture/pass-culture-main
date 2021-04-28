import '@testing-library/jest-dom'
import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'

import Filters from 'components/pages/Bookings/BookingsRecapTable/Filters/Filters'

jest.mock('utils/date', () => ({
  ...jest.requireActual('utils/date'),
  getToday: jest.fn().mockImplementation(() => new Date('2020-12-15T12:00:00Z')),
}))

describe('filter bookings by bookings period', () => {
  let props
  beforeEach(() => {
    props = {
      isLoading: false,
      offerVenue: 'all',
      oldestBookingDate: new Date(2020, 11, 14),
      updateGlobalFilters: jest.fn(),
    }
  })

  it('should select today as period ending date by default', async () => {
    // When
    render(<Filters {...props} />)

    // Then
    expect(await screen.findByDisplayValue('15/12/2020')).toBeInTheDocument()
  })

  it('should allow to select period ending date before today', async () => {
    // Given
    render(<Filters {...props} />)
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByText('14'))

    // Then
    expect(await screen.findByDisplayValue('14/12/2020')).toBeInTheDocument()
  })

  it('should not allow to select period ending date after today', async () => {
    // Given
    render(<Filters {...props} />)

    // When
    const periodEndingDateInput = await screen.findByDisplayValue('15/12/2020')
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should not allow to select period ending date before selected beginning date', async () => {
    // Given
    render(<Filters {...props} />)
    const periodBeginningDateInput = (await screen.findAllByPlaceholderText('JJ/MM/AAAA'))[1]
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('14'))
    const periodEndingDateInput = screen.getByDisplayValue('15/12/2020')

    // When
    fireEvent.click(periodEndingDateInput)
    fireEvent.click(screen.getByText('13'))

    // Then
    expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
  })

  it('should allow to select period beginning date before selected ending date', async () => {
    // Given
    render(<Filters {...props} />)
    const periodBeginningDateInput = screen.getAllByPlaceholderText('JJ/MM/AAAA')[1]

    // When
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('14'))

    // Then
    expect(await screen.findByDisplayValue('14/12/2020')).toBeInTheDocument()
  })

  it('should not allow to select period beginning date after ending date', async () => {
    // Given
    render(<Filters {...props} />)

    // When
    const periodBeginningDateInput = (await screen.findAllByPlaceholderText('JJ/MM/AAAA'))[1]
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('16'))

    // Then
    expect(screen.queryByDisplayValue('16/12/2020')).not.toBeInTheDocument()
  })

  it('should not allow to select period beginning date before oldest booking date', async () => {
    // Given
    render(<Filters {...props} />)

    // When
    const periodBeginningDateInput = (await screen.findAllByPlaceholderText('JJ/MM/AAAA'))[1]
    fireEvent.click(periodBeginningDateInput)
    fireEvent.click(screen.getByText('13'))

    // Then
    expect(screen.queryByDisplayValue('13/12/2020')).not.toBeInTheDocument()
  })
})
