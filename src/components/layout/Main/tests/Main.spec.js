import { shallow } from 'enzyme'
import React from 'react'

import Main from '../Main'

describe('src | components | layout | Main', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      children: [{}],
      currentUser: {},
      dispatch: jest.fn(),
      history: {},
      location: {},
      name: 'foo',
    }

    // when
    const wrapper = shallow(<Main {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
