import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import Tag from '../Tag'

describe('src | components | layout | Banner', () => {
  describe('render', () => {
    const label = 'Département'

    it('should display label', () => {
      // given
      render(<Tag>{label}</Tag>)

      // then
      expect(screen.getByText('Département')).toBeInTheDocument()
    })

    it('should close', async () => {
      const spyClose = vi.fn()
      const closeable = {
        closeLabel: 'Supprimer l’option',
        onClose: spyClose,
      }
      // given
      render(<Tag closeable={closeable}>{label}</Tag>)

      // when
      await userEvent.click(screen.getByTitle('Supprimer l’option'))

      // then
      expect(spyClose).toHaveBeenCalledTimes(1)
    })
  })
})
