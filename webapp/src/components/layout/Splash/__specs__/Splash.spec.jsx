import { shallow } from 'enzyme'
import React from 'react'
import { Transition } from 'react-transition-group'

import Splash from '../Splash'

describe('src | components | Splash', () => {
  let props

  beforeEach(() => {
    props = {
      closeTimeout: 1000,
      dispatch: jest.fn(),
      isBetaPage: true,
    }
  })

  it('should display a transition', () => {
    // when
    const wrapper = shallow(<Splash {...props} />)

    // then
    const transition = wrapper.find(Transition)
    expect(transition).toHaveLength(1)
  })
})
