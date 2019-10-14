import { shallow } from 'enzyme'
import React from 'react'

import Wallet from '../Wallet'

describe('src | components | layout | Verso | VersoControls | Wallet | Wallet', () => {
  it('should render a label and the amount of wallet', () => {
    // given
    const props = { value: 10 }

    // when
    const wrapper = shallow(<Wallet {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
