// jest --env=jsdom ./src/components/menu/tests/MenuHeader --watch
import React from 'react'
import { shallow } from 'enzyme'

import MenuHeader from '../MenuHeader'

const walletValueId = '#main-menu-header-wallet-value'

describe('src | components | menu | MenuHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        user: {
          publicName: 'username',
          wallet_balance: 500,
        },
      }

      // when
      const wrapper = shallow(<MenuHeader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('with no user', () => {
      // given
      const props = {}
      // when
      const wrapper = shallow(<MenuHeader {...props} />)
      const walletElement = wrapper.find(walletValueId).first()
      // then
      const expected = '--\u00A0€'
      const text = walletElement.text()
      expect(text).toEqual(expected)
    })
    it('with user but no wallet_balance', () => {
      // given
      const props = { user: {} }
      // when
      const wrapper = shallow(<MenuHeader {...props} />)
      const walletElement = wrapper.find(walletValueId).first()
      // then
      const expected = '--\u00A0€'
      const text = walletElement.text()
      expect(text).toEqual(expected)
    })
    it('with user and wallet_balance', () => {
      // given
      const props = { user: { wallet_balance: 500 } }
      // when
      const wrapper = shallow(<MenuHeader {...props} />)
      const walletElement = wrapper.find(walletValueId).first()
      // then
      const expected = '500\u00A0€'
      const text = walletElement.text()
      expect(text).toEqual(expected)
    })
  })
})
