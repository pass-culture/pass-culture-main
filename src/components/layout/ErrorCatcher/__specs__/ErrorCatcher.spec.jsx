import { shallow } from 'enzyme'
import React from 'react'

import ErrorCatcher from '../ErrorCatcher'

const routerProps = {
  history: { replace: jest.fn() },
}

describe('src | components | layout | ErrorCatcher', () => {
  it('should match the snapshot and render the children as is', () => {
    // given
    const props = { ...routerProps }
    const Children = () => (<span>
      {'any child component'}
    </span>)

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    ).dive()

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should match the snapshot with error', () => {
    // given
    const Children = () => null
    const props = { ...routerProps }
    const error = new Error('This is an error!')

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    )
    wrapper.find(Children).simulateError(error)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('do not render childrend if an error is throwned', () => {
    // given
    const Children = () => null
    const props = { ...routerProps }
    const error = new Error('This is an error!')

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    )
    wrapper.find(Children).simulateError(error)

    // then
    expect(Children).toHaveLength(0)
  })

  it('render catcher view if an error is throwned', () => {
    // given
    const Children = () => null
    const props = { ...routerProps }
    const error = new Error('This is an error!')

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    )
    wrapper.find(Children).simulateError(error)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
