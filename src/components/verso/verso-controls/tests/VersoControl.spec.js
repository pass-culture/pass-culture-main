import React from 'react'
import { shallow } from 'enzyme'
import VersoControl from '../VersoControl'

import Finishable from '../../../layout/Finishable'
import CancelButton from '../booking/cancel-this/CancelThisContainer'
import BookThisButton from '../booking/book-this/BookThisContainer'

describe('src | components | verso | verso-controls | VersoControl', () => {
  it('should render component with a bookable offer', () => {
    // given
    const props = { booking: null, isFinished: false }

    // when
    const wrapper = shallow(<VersoControl {...props} />)
    const finishable = wrapper.find(Finishable)
    const cancel = wrapper.find(CancelButton)
    const bookThis = wrapper.find(BookThisButton)
    const blocker = wrapper.find('.finishable-click-blocker')

    // then
    expect(blocker).toHaveLength(0)
    expect(finishable).toHaveLength(1)
    expect(finishable.prop('finished')).toBe(false)
    expect(cancel).toHaveLength(0)
    expect(bookThis).toHaveLength(1)
  })

  it('should render component with a already booked/cancellable offer', () => {
    // given
    const props = { booking: {}, isFinished: false }

    // when
    const wrapper = shallow(<VersoControl {...props} />)
    const finishable = wrapper.find(Finishable)
    const cancel = wrapper.find(CancelButton)
    const bookthis = wrapper.find(BookThisButton)
    const blocker = wrapper.find('.finishable-click-blocker')

    // then
    expect(blocker).toHaveLength(0)
    expect(finishable).toHaveLength(1)
    expect(finishable.prop('finished')).toBe(false)
    expect(cancel).toHaveLength(1)
    expect(bookthis).toHaveLength(0)
  })

  it('should render component with a already booked/cancellable offer', () => {
    // given
    const props = { booking: {}, isFinished: true }

    // when
    const wrapper = shallow(<VersoControl {...props} />)
    const finishable = wrapper.find(Finishable)
    const cancel = wrapper.find(CancelButton)
    const bookthis = wrapper.find(BookThisButton)
    const blocker = wrapper.find('.finishable-click-blocker')

    // then
    expect(blocker).toHaveLength(1)
    expect(finishable).toHaveLength(1)
    expect(finishable.prop('finished')).toBe(true)
    expect(cancel).toHaveLength(1)
    expect(bookthis).toHaveLength(0)
  })
})
