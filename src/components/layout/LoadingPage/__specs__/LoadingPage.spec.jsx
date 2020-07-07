import { shallow } from 'enzyme'
import React from 'react'

import LoadingPage from '../LoadingPage'
import { Animation } from '../../../pages/create-account/Animation/Animation'

describe('loading page', () => {
  it('should render the loading animation', () => {
    // when
    const wrapper = shallow(<LoadingPage />)

    // then
    const loadingAnimation = wrapper.find(Animation)
    expect(loadingAnimation).toHaveLength(1)
    expect(loadingAnimation.prop('loop')).toBe(true)
    expect(loadingAnimation.prop('name')).toBe('loading-animation')
  })

  it('should render the loading message', () => {
    // when
    const wrapper = shallow(<LoadingPage />)

    // then
    const loadingMessage = wrapper.find({ children: 'Chargement en cours…' })
    expect(loadingMessage.exists()).toBe(true)
  })
})
