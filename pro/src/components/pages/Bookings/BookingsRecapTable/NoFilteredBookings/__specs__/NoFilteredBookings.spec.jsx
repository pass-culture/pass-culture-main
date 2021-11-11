/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt rtl "Gaël: migration from enzyme to RTL"
*/

import { shallow } from 'enzyme'
import React from 'react'

import NoFilteredBookings from '../NoFilteredBookings'

describe('components | NoFilteredBookings', () => {
  it('should reset filters when clicking on reset button', () => {
    // given
    const props = {
      resetFilters: jest.fn(),
    }
    const wrapper = shallow(<NoFilteredBookings {...props} />)
    const resetButton = wrapper.find({ children: 'afficher toutes les réservations' })

    // when
    resetButton.simulate('click')

    // then
    expect(props.resetFilters).toHaveBeenCalledTimes(1)
  })
})
