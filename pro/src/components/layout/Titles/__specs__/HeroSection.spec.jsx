import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import Titles from '../Titles'

describe('src | components | layout | Titles', () => {
  describe('render', () => {
    describe('subtitle', () => {
      it('should display subtitle when given', () => {
        // given
        const props = {
          subtitle: 'Fake subtitle',
          title: 'Fake title',
        }

        // when
        render(<Titles {...props} />)

        // then
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(
          'FAKE SUBTITLE'
        )
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
          'Fake title'
        )
      })
    })
  })
})
