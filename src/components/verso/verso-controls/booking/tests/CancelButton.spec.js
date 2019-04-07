// $(yarn bin)/jest --env=jsdom src/components/verso/verso-controls/booking/tests/CancelButton.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'
import { RawCancelButton } from '../CancelButton'
import Price from '../../../../layout/Price'

const defaultprops = {
  booking: {},
  dispatch: jest.fn(),
  history: {},
  isCancelled: false,
  locationSearch: '?astring',
  priceValue: 42,
}

describe('src | components | verso | verso-controls | booking | RawCancelButton', () => {
  describe('snapshot with required props', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RawCancelButton {...defaultprops} />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('contains price, check-icon, label', () => {
      // when
      const wrapper = shallow(<RawCancelButton {...defaultprops} />)
      const price = wrapper.find(Price)
      const icon = wrapper.find('.icon-ico-check')
      const label = wrapper.find('.pc-ticket-button-label')
      // then
      expect(icon).toHaveLength(1)
      expect(price).toHaveLength(1)
      expect(label).toHaveLength(1)
    })
    it('do not contains check icon', () => {
      // given
      const props = { ...defaultprops, isCancelled: true }
      // when
      const wrapper = shallow(<RawCancelButton {...props} />)
      const icon = wrapper.find('.icon-ico-check')
      // then
      expect(icon).toHaveLength(0)
    })
  })
})
