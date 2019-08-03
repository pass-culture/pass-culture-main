import { shallow } from 'enzyme'
import React from 'react'

import Header from '../Header'

describe('src | components | menu | Header', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {
        publicName: 'Emmanuel Macron',
        wallet_balance: 500,
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    const wrapper = shallow(<Header {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should render the username and his wallet', () => {
      // given
      const wrapper = shallow(<Header {...props} />)

      // when
      const walletElement = wrapper.find('#main-menu-header-wallet-value').text()
      const username = wrapper.find('#main-menu-header-username').text()

      // then
      expect(walletElement).toBe('500\u00A0€')
      expect(username).toBe('Emmanuel Macron')
    })
  })
})
