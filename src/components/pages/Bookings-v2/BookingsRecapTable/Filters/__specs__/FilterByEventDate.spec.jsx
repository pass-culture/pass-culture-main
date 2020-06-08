import FilterByEventDate from '../FilterByEventDate.jsx'
import React from 'react'
import { shallow } from 'enzyme'
import moment from 'moment/moment'

describe('components | FilterByEventDate', () => {
  let props
  beforeEach(() => {
    props = {
      onHandleOfferDateChange: jest.fn(),
      selectedOfferDate: null,
    }
  })

  it('should display a DatePicker', async () => {
    // When
    const wrapper = shallow(<FilterByEventDate {...props} />)

    // Then
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' })
    expect(offerDateInput).toHaveLength(1)
  })

  it('should apply offerDate filter when choosing an offer date', async () => {
    // Given
    const selectedDate = moment('2020-05-20')
    const wrapper = shallow(<FilterByEventDate {...props} />)
    const offerDateInput = wrapper.find({ placeholderText: 'JJ/MM/AAAA' }).at(0)

    // When
    await offerDateInput.simulate('change', selectedDate)

    // Then
    expect(props.onHandleOfferDateChange).toHaveBeenCalledWith(selectedDate)
  })
})
