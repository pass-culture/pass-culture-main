import { shallow } from 'enzyme'
import React from 'react'

import NotMatch from '../NotMatch'

describe('notMatch', () => {
  let props

  beforeEach(() => {
    props = {
      delay: 1,
      location: {},
      redirect: '/fake-url',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NotMatch {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
