import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import NoFilteredBookings from '../NoFilteredBookings'

describe('components | NoFilteredBookings', () => {
  it('should reset filters when clicking on reset button', async () => {
    // given
    const props = {
      resetFilters: jest.fn(),
    }
    render(<NoFilteredBookings {...props} />)
    const resetButton = screen.getByText('afficher toutes les réservations')

    // when
    await userEvent.click(resetButton)

    // then
    expect(props.resetFilters).toHaveBeenCalledTimes(1)
  })
})
