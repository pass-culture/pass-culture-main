import React from 'react'
import { shallow } from 'enzyme'

import SliderPoints from '../SliderPoints'

describe('components | SliderPoints', () => {
  it('should display as much bullets as there are elements', () => {
    // given
    const elements = ['Apple', 'Banana', 'Kiwi']
    const currentStep = 0

    const props = {
      elements, currentStep
    }

    // when
    const wrapper = shallow(<SliderPoints {...props} />)
    const sliderPoints = wrapper.find('.slider-point')

    // then
    expect(sliderPoints).toHaveLength(elements.length)
  })

  it('should have className `filled` when index is same as currentStep', () => {
    // given
    const elements = ['Apple', 'Banana', 'Kiwi', 'Ananas']
    const currentStep = 2

    const props = {
      elements, currentStep
    }

    // when
    const wrapper = shallow(<SliderPoints {...props} />)

    // then
    expect(wrapper.find('.slider-point').get(2).props.className).toContain('filled')
  })
})
