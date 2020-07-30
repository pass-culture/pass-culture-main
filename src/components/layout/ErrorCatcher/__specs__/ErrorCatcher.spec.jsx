import { shallow } from 'enzyme'
import React from 'react'

import ErrorCatcher from '../ErrorCatcher'

describe('src | components | ErrorCatcher', () => {
  it('should display the children as is', () => {
    // given
    const props = {
      history: { replace: jest.fn() },
    }
    const Children = () => (<span>
      {'any child component'}
    </span>)

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    )

    // then
    const children = wrapper.find(Children)
    expect(children).toHaveLength(1)
  })

  it('do not render childrend if an error is throwned', () => {
    // given
    const Children = () => null
    const props = {
      history: { replace: jest.fn() },
    }
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
    const props = {
      history: { replace: jest.fn() },
    }
    const error = new Error('This is an error!')

    // when
    const wrapper = shallow(
      <ErrorCatcher {...props}>
        <Children />
      </ErrorCatcher>
    )
    wrapper.find(Children).simulateError(error)

    // then
    const sentence = wrapper.find({ children: 'Une erreur est survenue.' })
    const button = wrapper.find('button').find({ children: 'Retour aux offres' })
    expect(sentence).toHaveLength(1)
    expect(button).toHaveLength(1)
  })
})
