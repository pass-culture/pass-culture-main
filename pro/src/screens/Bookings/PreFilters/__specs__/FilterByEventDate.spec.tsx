import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { EMPTY_FILTER_VALUE } from 'core/Bookings'

import FilterByEventDate, { FilterByEventDateProps } from '../FilterByEventDate'

describe('components | FilterByEventDate', () => {
  let props: FilterByEventDateProps
  beforeEach(() => {
    props = {
      updateFilters: jest.fn(),
      selectedOfferDate: EMPTY_FILTER_VALUE,
    }
  })

  it('should display a DatePicker', async () => {
    // When
    render(<FilterByEventDate {...props} />)

    // Then
    expect(screen.getByPlaceholderText('JJ/MM/AAAA')).toBeInTheDocument()
  })

  it('should apply offerDate filter when choosing an offer date', async () => {
    // Given
    const selectedDate = new Date('2020-05-20')
    render(<FilterByEventDate {...props} />)
    const offerDateInput = screen.getByPlaceholderText('JJ/MM/AAAA')

    // When
    await userEvent.type(offerDateInput, selectedDate.toISOString())

    // Then
    expect(props.updateFilters).toHaveBeenCalledWith({
      offerEventDate: selectedDate,
    })
  })
})
