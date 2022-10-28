import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import Insert from '../Insert'

describe('src | components | layout | Insert', () => {
  let props

  beforeEach(() => {
    props = {
      children: `I'm a child`,
      icon: 'example-icon-name',
    }
  })

  describe('render', () => {
    it('should render an Icon', () => {
      // when
      render(<Insert {...props} />)

      // then
      expect(screen.getByRole('img')).toBeInTheDocument()
    })

    it('should render a children', () => {
      // when
      render(<Insert {...props} />)

      // then
      expect(screen.getByText("I'm a child")).toBeInTheDocument()
    })
  })
})
