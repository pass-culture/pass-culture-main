import React from 'react'
import { shallow } from 'enzyme'

import PickByDate from '../PickByDate'

describe('src | components | pages | search | PickByDate', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dateFormat: '',
        filterDate: jest.fn(),
        highlightedDates: '',
        id: '',
        maxDate: '',
        minDate: '',
        size: '',
        value: '',
      }

      // when
      const wrapper = shallow(<PickByDate {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
