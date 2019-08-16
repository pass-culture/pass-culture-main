import React from 'react'
import { shallow } from 'enzyme'

import Recto from '../Recto'

describe('src | components | recto | Recto', () => {
  it('should match the snapshot with required props only', () => {
    // given
    const props = {
      areDetailsVisible: true,
    }

    // when
    const wrapper = shallow(<Recto {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
