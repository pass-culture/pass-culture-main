import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import Icon from '../Icon'

describe('src | components | layout | Icon', () => {
  describe('render', () => {
    it('should render an image with correct props when svg given', () => {
      // when
      render(<Icon svg="picto-svg" />)

      // then
      const image = screen.getByRole('img')
      expect(image).toHaveAttribute('alt', '')
      expect(image).toHaveAttribute(
        'src',
        expect.stringContaining('picto-svg.svg')
      )
    })

    it('should render an image with correct props when png given', () => {
      // when
      render(<Icon png="icon-png" />)

      // then
      const image = screen.getByRole('img')
      expect(image).toHaveAttribute('alt', '')
      expect(image).toHaveAttribute(
        'src',
        expect.stringContaining('icon-png.png')
      )
    })

    it('should render an image with alt when given', () => {
      // when
      render(<Icon alt="Some alternate title" />)

      // then
      const image = screen.getByRole('img')
      expect(image).toHaveAttribute('alt', 'Some alternate title')
    })
  })
})
