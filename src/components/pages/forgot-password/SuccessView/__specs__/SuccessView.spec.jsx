import React from 'react'
import { shallow } from 'enzyme'
import SuccessView from '../SuccessView'

describe('src | components | pages | forgot-password | SuccessView', () => {
  it('should match the snapshot without token', () => {
    // given
    const props = { token: null }

    // when
    const wrapper = shallow(<SuccessView {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot with token', () => {
    // given
    const props = { token: '1234567890' }

    // when
    const wrapper = shallow(<SuccessView {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
