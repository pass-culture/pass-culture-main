import { render, screen } from '@testing-library/react'

import { Tag, TagVariant } from '../Tag'

describe('Tag', () => {
  describe('render', () => {
    it.each([
      TagVariant.SMALL_OUTLINE,
      TagVariant.LIGHT_GREY,
      TagVariant.DARK_GREY,
      TagVariant.BLACK,
      TagVariant.LIGHT_PURPLE,
      TagVariant.PURPLE,
      TagVariant.RED,
      TagVariant.GREEN,
    ])('should display label for variant: %s', (variant) => {
      render(<Tag variant={variant}>Département</Tag>)

      expect(screen.getByText('Département')).toBeInTheDocument()
    })
  })
})
