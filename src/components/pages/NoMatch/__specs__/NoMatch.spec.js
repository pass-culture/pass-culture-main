import React from 'react'
import { shallow } from 'enzyme'
import NoMatch from '../NoMatch'

describe('src | components | pages | NoMatch', () => {
  let props

  beforeEach(() => {
    props = {
      location: {
        pathname: '/fake-url'
      }
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<NoMatch {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
