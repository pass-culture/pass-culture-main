import { render, screen } from '@testing-library/react'
import React from 'react'

import { BookingDateCell, BookingDateCellProps } from '../BookingDateCell'

const renderDateCell = (props: BookingDateCellProps) =>
  render(<BookingDateCell {...props} />)

describe('BookingDateCell', () => {
  it('should display the date and the time', () => {
    const props = {
      bookingDateTimeIsoString: '2020-04-03T12:00:00+04:00',
      amount: 50,
      priceCategoryLabel: 'Tarif Or',
    }

    renderDateCell(props)

    expect(screen.getByText('03/04/2020')).toBeInTheDocument()
    expect(screen.getByText('12:00')).toBeInTheDocument()
    expect(screen.getByText('50 €')).toBeInTheDocument()
    expect(screen.getByText('Tarif Or')).toBeInTheDocument()
  })
})
