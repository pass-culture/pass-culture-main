import { render, screen } from '@testing-library/react'

import { BookingDateCell, BookingDateCellProps } from '../BookingDateCell'

const renderDateCell = (props: BookingDateCellProps) =>
  render(<BookingDateCell {...props} />)

describe('BookingDateCell', () => {
  it('should display the date and the time', () => {
    const props = {
      bookingDateTimeIsoString: '2020-04-03T12:00:00+04:00',
    }

    renderDateCell(props)

    expect(screen.getByText('03/04/2020')).toBeInTheDocument()
    expect(screen.getByText('12:00')).toBeInTheDocument()
  })
})
