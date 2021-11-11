import React from 'react'
import { shallow } from 'enzyme'
import Draggable from 'react-draggable'

import DraggableTutorial from '../DraggableTutorial'

describe('components | DraggableTutorial', () => {
  it('should display a draggable div', () => {
    // given
    const props = {
      children: <div />,
      handleGoNext: jest.fn(),
      handleGoPrevious: jest.fn(),
      step: 3,
    }

    // when
    const wrapper = shallow(<DraggableTutorial {...props} />)

    // then
    const draggable = wrapper.find(Draggable)
    expect(draggable).toHaveLength(1)
  })

  describe('calculateBounds()', () => {
    it('should block dragging to the left when first tutorial is displayed', () => {
      // given
      const props = {
        children: <div />,
        handleGoNext: jest.fn(),
        handleGoPrevious: jest.fn(),
        step: 0,
      }

      // when
      const wrapper = shallow(<DraggableTutorial {...props} />)
      const draggable = wrapper.find(Draggable)
      // then
      expect(draggable.prop('bounds').right).toBe(0)
    })

    it('should not block left or right dragging when displayed tutorial is not the first one', () => {
      // given
      const props = {
        children: <div />,
        handleGoNext: jest.fn(),
        handleGoPrevious: jest.fn(),
        step: 2,
      }

      // when
      const wrapper = shallow(<DraggableTutorial {...props} />)
      const draggable = wrapper.find(Draggable)
      // then
      expect(draggable.prop('bounds').right).toBeUndefined()
      expect(draggable.prop('bounds').left).toBeUndefined()
    })
  })
})
