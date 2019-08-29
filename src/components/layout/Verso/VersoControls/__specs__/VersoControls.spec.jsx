import React from 'react'
import { shallow } from 'enzyme'
import VersoControls from '../VersoControls'

import FinishableContainer from '../../../Finishable/FinishableContainer'
import CancelButton from '../booking/CancelThisLink/CancelThisLinkContainer'
import BookThisButton from '../booking/BookThisLink/BookThisLinkContainer'

describe('src | components | layout | Verso | VersoControls | VersoControls', () => {
  it('should render component with a bookable offer', () => {
    // given
    const props = {
      showCancelView: false
    }

    // when
    const wrapper = shallow(<VersoControls {...props} />)
    const finishable = wrapper.find(FinishableContainer)
    const cancel = wrapper.find(CancelButton)
    const bookThis = wrapper.find(BookThisButton)

    // then
    expect(finishable).toHaveLength(1)
    expect(cancel).toHaveLength(0)
    expect(bookThis).toHaveLength(1)
  })

  it('should render component with a already booked/cancellable offer', () => {
    // given
    const props = {
      showCancelView: true
    }

    // when
    const wrapper = shallow(<VersoControls {...props} />)
    const finishable = wrapper.find(FinishableContainer)
    const cancel = wrapper.find(CancelButton)
    const bookthis = wrapper.find(BookThisButton)

    // then
    expect(finishable).toHaveLength(1)
    expect(cancel).toHaveLength(1)
    expect(bookthis).toHaveLength(0)
  })

  it('should render component with a already booked/cancellable offer (réécrire)', () => {
    // given
    const props = {
      showCancelView: true
    }

    // when
    const wrapper = shallow(<VersoControls {...props} />)
    const finishable = wrapper.find(FinishableContainer)
    const cancel = wrapper.find(CancelButton)
    const bookthis = wrapper.find(BookThisButton)

    // then
    expect(finishable).toHaveLength(1)
    expect(cancel).toHaveLength(1)
    expect(bookthis).toHaveLength(0)
  })
})
