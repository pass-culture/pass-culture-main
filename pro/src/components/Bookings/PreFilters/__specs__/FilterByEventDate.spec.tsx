import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { EMPTY_FILTER_VALUE } from 'commons/core/Bookings/constants'

import { FilterByEventDate, FilterByEventDateProps } from '../FilterByEventDate'

describe('components | FilterByEventDate', () => {
  let props: FilterByEventDateProps
  beforeEach(() => {
    props = {
      updateFilters: vi.fn(),
      selectedOfferDate: EMPTY_FILTER_VALUE,
    }
  })

  it('should display a DatePicker', () => {
    render(<FilterByEventDate {...props} />)

    expect(screen.getByPlaceholderText('JJ/MM/AAAA')).toBeInTheDocument()
  })

  it('should apply offerDate filter when choosing an offer date', async () => {
    const selectedDate = '2020-05-20'
    render(<FilterByEventDate {...props} />)
    const offerDateInput = screen.getByPlaceholderText('JJ/MM/AAAA')

    await userEvent.type(offerDateInput, selectedDate)

    expect(props.updateFilters).toHaveBeenCalledWith({
      offerEventDate: selectedDate,
    })
  })
})
