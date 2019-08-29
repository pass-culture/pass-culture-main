import { shallow } from 'enzyme'
import FilterByVenue from '../FilterByVenue'
import React from 'react'
import FilterByDate from "../../FilterByDate/FilterByDate";

describe('src | components | pages | Bookings | FilterByVenue', () => {
  let props

  beforeEach(() => {
    props = {
      isDigital: false,
      loadVenues: jest.fn(),
      updateVenueId: jest.fn(),
      updateIsFilteredByDigitalVenues: jest.fn(),
      venuesOptions:
        [
          {
            id: 'all',
            name: 'Toutes les offres',
          },
          {
            id: 1,
            name: 'Babar',
          },
          {
            id: 2,
            name: 'Céleste',
          }],
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<FilterByVenue {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a select input for venue with 4 options', () => {
      // given
      props.isDigital = false

      // when
      const wrapper = shallow(<FilterByVenue {...props} />)

      // then
      const selectVenue = wrapper.find('#venues')
      expect(selectVenue.prop('className')).toBe('pc-selectbox')
      expect(selectVenue.prop('id')).toBe('venues')
      expect(selectVenue.prop('onBlur')).toStrictEqual(expect.any(Function))
      expect(selectVenue.prop('onChange')).toStrictEqual(expect.any(Function))
      const options = selectVenue.find('option')
      expect(options).toHaveLength(4)
      expect(options.at(0).prop('disabled')).toBe(true)
      expect(options.at(0).prop('label')).toBe(' - Choisissez un lieu dans la liste - ')
      expect(options.at(0).prop('selected')).toBe(true)
      expect(options.at(1).key()).toBe('all')
      expect(options.at(1).prop('value')).toBe('all')
      expect(options.at(2).key()).toBe('1')
      expect(options.at(2).prop('value')).toBe(1)
      expect(options.at(3).key()).toBe('2')
      expect(options.at(3).prop('value')).toBe(2)
    })
  })
})
