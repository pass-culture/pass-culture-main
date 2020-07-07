import { mount } from 'enzyme'
import lottie from 'lottie-web'
import React from 'react'
import { Animation } from '../Animation'

jest.mock('../../../../../utils/config', () => {
  return { ANIMATIONS_URL: 'path/to/animations' }
})

describe('animation', () => {
  it('should render an animation', () => {
    // Given
    jest.spyOn(lottie, 'loadAnimation')

    // When
    mount(<Animation
      loop
      name="animation"
          />)

    // Then
    expect(lottie.loadAnimation).toHaveBeenCalledWith({
      container: expect.any(HTMLDivElement),
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: `path/to/animations/animation.json`,
    })
  })

  it('should set animation speed', () => {
    // Given
    const setSpeed = jest.fn()
    jest.spyOn(lottie, 'loadAnimation').mockReturnValue({
      setSpeed: setSpeed,
    })

    // When
    mount(<Animation
      name="animation"
      speed={0.7}
          />)

    // Then
    expect(setSpeed).toHaveBeenCalledWith(0.7)
  })
})
