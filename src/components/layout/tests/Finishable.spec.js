import React from 'react'
import { shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'

import Finishable from '../Finishable'

describe('src | components | layout | Finishable', () => {
  const finishableClass = '.finishable'

  it('should match snapshot with required props', () => {
    // given
    const props = {
      children: <div>cette offre n&apos;est pas terminée</div>,
    }

    // when
    const wrapper = shallow(<Finishable {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should not contains finishable element', () => {
    // given
    const props = {
      children: (
        <div className="content">cette offre n&apos;est pas terminée</div>
      ),
    }

    // when
    const wrapper = shallow(<Finishable {...props} />)
    const content = wrapper.find('.content')
    const icon = wrapper.find(Icon)
    const finishable = wrapper.find(finishableClass)

    // then
    expect(content).toHaveLength(1)
    expect(icon).toHaveLength(0)
    expect(finishable).toHaveLength(0)
  })

  it('should contains finishable element', () => {
    // given
    const props = {
      children: <div className="content">cette offre est terminée</div>,
      finished: true,
    }

    // when
    const wrapper = shallow(<Finishable {...props} />)
    const content = wrapper.find('.content')
    const icon = wrapper.find(Icon)
    const finishable = wrapper.find(finishableClass)

    // then
    expect(content).toHaveLength(1)
    expect(icon).toHaveLength(1)
    expect(finishable).toHaveLength(1)
  })
})
