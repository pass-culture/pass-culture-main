import { render, screen } from '@testing-library/react'
import React from 'react'

import Tag from '../Tag'

describe('Tag', () => {
  describe('render', () => {
    it('should display label', () => {
      render(<Tag>Département</Tag>)

      expect(screen.getByText('Département')).toBeInTheDocument()
    })
  })
})
