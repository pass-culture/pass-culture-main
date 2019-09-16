import React from 'react'
import { shallow } from 'enzyme'
import NotMatch from '../NotMatch'

describe('src | components | pages | NotMatch', () => {
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
