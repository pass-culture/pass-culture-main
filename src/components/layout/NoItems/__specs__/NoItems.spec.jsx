import { shallow } from 'enzyme'
import React from 'react'

import NoItems from '../NoItems'

describe('src | components | layout | NoItems', () => {
  it('should match the snapshot', () => {
    //given
    const props = {
      sentence: "Une phrase d'accroche",
    }

    // when
    const wrapper = shallow(<NoItems {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
