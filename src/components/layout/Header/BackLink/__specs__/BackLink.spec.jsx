import { shallow } from 'enzyme'
import React from 'react'

import BackLink from '../BackLink'

describe('src | components | layout | Header | BackLink', () => {
  let props

  beforeEach(() => {
    props = {
      backTo: '/fake-url',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<BackLink {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
