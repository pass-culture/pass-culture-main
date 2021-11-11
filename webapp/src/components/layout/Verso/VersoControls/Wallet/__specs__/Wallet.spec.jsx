import { shallow } from 'enzyme'
import React from 'react'

import Wallet from '../Wallet'

describe('src | components | Wallet', () => {
  it('should render a label and the amount of wallet', () => {
    // given
    const props = {
      value: 10,
    }

    // when
    const wrapper = shallow(<Wallet {...props} />)

    // then
    const sentence = wrapper.find({ children: 'Mon pass' })
    const price = wrapper.find({ children: '10 €' })
    expect(sentence).toHaveLength(1)
    expect(price).toHaveLength(1)
  })
})
