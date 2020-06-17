import { mount } from 'enzyme'
import React from 'react'
import { Helmet } from 'react-helmet'

import {
  black as defaultColor,
  primary as primaryColor,
} from '../../../../styles/variables/index.scss'
import { isAppInFullscreen } from '../domain/isAppInFullscreen'
import { shouldStatusBarBeColored } from '../domain/shouldStatusBarBeColored'
import { StatusBarHelmet } from '../StatusBarHelmet'

jest.mock('../domain/isAppInFullscreen', () => {
  return { isAppInFullscreen: jest.fn() }
})

jest.mock('../domain/shouldStatusBarBeColored', () => {
  return { shouldStatusBarBeColored: jest.fn() }
})

jest.mock('../../../../styles/variables/index.scss', () => {
  return { primary: 'primaryColor', black: 'defaultColor' }
})

describe('helmet status bar component', () => {
  describe('when app is not in fullscreen', () => {
    it('should render only iOS meta tag', () => {
      // Given
      const coloredHeaderPath = '/path/with/colored/header'
      isAppInFullscreen.mockReturnValue(false)
      shouldStatusBarBeColored.mockReturnValue(true)

      // When
      const wrapper = mount(<StatusBarHelmet pathname={coloredHeaderPath} />)

      // Then
      const helmetChildren = wrapper.find(Helmet).props().children
      expect(helmetChildren[0].type).toBe('meta')
      expect(helmetChildren[0].props.content).toBe('black-translucent')
      expect(helmetChildren[0].props.name).toBe('apple-mobile-web-app-status-bar-style')
      expect(helmetChildren[1]).toBe(false)
      expect(helmetChildren[2]).toBe(false)
    })
  })

  describe('when app is in fullscreen', () => {
    beforeEach(() => {
      isAppInFullscreen.mockReturnValue(true)
    })

    it('should render body with background color and meta tag for theme color', () => {
      // Given
      const coloredStatusBarPath = '/any/path'
      shouldStatusBarBeColored.mockReturnValue(expect.any(Boolean))

      // When
      const wrapper = mount(<StatusBarHelmet pathname={coloredStatusBarPath} />)

      // Then
      const helmetChildren = wrapper.find(Helmet).props().children
      expect(helmetChildren).toHaveLength(3)
      expect(helmetChildren[0].type).toBe('meta')
      expect(helmetChildren[0].props.content).toBe('black-translucent')
      expect(helmetChildren[0].props.name).toBe('apple-mobile-web-app-status-bar-style')
      expect(helmetChildren[1].type).toBe('body')
      expect(helmetChildren[2].type).toBe('meta')
      expect(helmetChildren[2].props.name).toBe('theme-color')
      expect(shouldStatusBarBeColored).toHaveBeenCalledWith(coloredStatusBarPath)
    })

    it('should set primary color in status bar if it should be colored given current path', () => {
      // Given
      const coloredStatusBarPath = '/path/with/colored/status/bar'
      shouldStatusBarBeColored.mockReturnValue(true)

      // When
      const wrapper = mount(<StatusBarHelmet pathname={coloredStatusBarPath} />)

      // Then
      const helmetChildren = wrapper.find(Helmet).props().children

      expect(helmetChildren[1].props.style).toBe(`background-color:${primaryColor};`)
      expect(helmetChildren[2].props.content).toBe(primaryColor)
    })

    it('should set default color in status bar if it should not be colored given current path', () => {
      // Given
      const nonColoredStatusBarPath = '/path/with/non/colored/status/bar'
      shouldStatusBarBeColored.mockReturnValue(false)

      // When
      const wrapper = mount(<StatusBarHelmet pathname={nonColoredStatusBarPath} />)

      // Then
      const helmetChildren = wrapper.find(Helmet).props().children

      expect(helmetChildren[1].props.style).toBe(`background-color:${defaultColor};`)
      expect(helmetChildren[2].props.content).toBe(defaultColor)
    })
  })
})
