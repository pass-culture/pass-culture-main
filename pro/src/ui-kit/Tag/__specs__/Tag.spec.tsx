import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import React from 'react'
import Tag from '../Tag'
import userEvent from '@testing-library/user-event'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    const label = 'Département'

    it('should display label', () => {
      // given
      render(<Tag label={label} />)

      // then
      expect(screen.getByText('Département')).toBeInTheDocument()
    })

    it('should close', async () => {
      const spyClose = jest.fn()
      const closeable = {
        closeLabel: 'Supprimer l’option',
        onClose: spyClose,
      }
      // given
      render(<Tag label={label} closeable={closeable} />)

      // when
      await userEvent.click(screen.getByAltText('Supprimer l’option'))

      // then
      expect(spyClose).toHaveBeenCalledTimes(1)
    })
  })
})
