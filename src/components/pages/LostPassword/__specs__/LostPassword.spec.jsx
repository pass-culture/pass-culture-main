import React from 'react'
import { shallow } from 'enzyme'
import LostPassword from '../LostPassword'

describe('src | components | pages | LostPassword', () => {
  let props

  beforeEach(() => {
    props = {
      change: false,
      envoye: false,
      errors: {},
      token: 'ABC',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<LostPassword {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
