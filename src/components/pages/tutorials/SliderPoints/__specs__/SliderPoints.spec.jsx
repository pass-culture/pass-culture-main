import React from 'react'
import { shallow } from 'enzyme'

import SliderPoints from '../SliderPoints'

describe('components | SliderPoints', () => {
  it('should have as much bullet points as there are elements and current step point should be filled', () => {
    // given
    const elements = ['Apple', 'Banana', 'Kiwi', 'Ananas']
    const currentStep = 2

    const props = {
      elements,
      currentStep,
    }

    // when
    const wrapper = shallow(<SliderPoints {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
