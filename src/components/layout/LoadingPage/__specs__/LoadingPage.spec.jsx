import { shallow } from 'enzyme'
import React from 'react'
import LoadingPage from '../LoadingPage'
import LoadingAnimation from '../LoadingAnimation/LoadingAnimation'

describe('src | layout | LoadingPage', () => {
  it('should render the loading animation', () => {
    // when
    const wrapper = shallow(<LoadingPage />)

    // then
    const loadingAnimation = wrapper.find(LoadingAnimation)
    expect(loadingAnimation).toHaveLength(1)
  })

  it('should render the loading message', () => {
    // when
    const wrapper = shallow(<LoadingPage />)

    // then
    const loadingMessage = wrapper.find({ children: 'Chargement en cours ...' })
    expect(loadingMessage.exists()).toBe(true)
  })
})
