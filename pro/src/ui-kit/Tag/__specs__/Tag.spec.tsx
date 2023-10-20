import { render, screen } from '@testing-library/react'
import React from 'react'

import { Tag, TagVariant } from '../Tag'

describe('Tag', () => {
  describe('render', () => {
    it.each([TagVariant.SMALL_OUTLINE, TagVariant.GREY])(
      'should display label for variant: %s',
      (variant) => {
        render(<Tag variant={variant}>Département</Tag>)

        expect(screen.getByText('Département')).toBeInTheDocument()
      }
    )
  })
})
