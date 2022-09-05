import '@testing-library/jest-dom'
import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'

import { EMPTY_FILTER_VALUE } from 'core/Bookings'

import FilterByEventDate, {
  IFilterByEventDateProps,
} from '../FilterByEventDate'

describe('components | FilterByEventDate', () => {
  let props: IFilterByEventDateProps
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
    fireEvent.change(offerDateInput, { target: { value: selectedDate } })
    // Then
    expect(props.updateFilters).toHaveBeenCalledWith({
      offerEventDate: selectedDate,
    })
  })
})
