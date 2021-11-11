import { shallow } from 'enzyme'
import React from 'react'

import SliderPoints from '../SliderPoints'

describe('components | SliderPoints', () => {
  it('should have as much bullet points as there are elements and current step point should be filled', () => {
    // given
    const maxStep = 4
    const currentStep = 2

    const props = {
      maxStep,
      currentStep,
    }

    // when
    const wrapper = shallow(<SliderPoints {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
