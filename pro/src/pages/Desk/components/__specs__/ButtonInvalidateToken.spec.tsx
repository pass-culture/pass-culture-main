import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { ButtonInvalidateToken } from '../ButtonInvalidateToken'

vi.mock('@/commons/hooks/useMediaQuery', () => ({
  useMediaQuery: vi.fn(() => false),
  TABLET_MEDIA_QUERY: '(max-width: 37.5rem)',
}))

const setup = () => {
  const onConfirm = vi.fn()

  const renderResult = render(<ButtonInvalidateToken onConfirm={onConfirm} />)

  const openDialog = async () => {
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Invalider la contremarque',
      })
    )
  }

  return { ...renderResult, onConfirm, openDialog }
}

describe('ButtonInvalidateToken', () => {
  describe('dialog opening', () => {
    it('should render without accessibility violations', async () => {
      const { container } = setup()

      expect(await axe(container)).toHaveNoViolations()
    })

    it('opens confirmation dialog when clicking invalidate button', async () => {
      const { openDialog } = setup()

      await openDialog()

      expect(screen.getByRole('dialog')).toBeInTheDocument()

      expect(
        screen.getByText('Voulez-vous vraiment invalider cette contremarque ?')
      ).toBeInTheDocument()
    })
  })

  describe('dialog closing', () => {
    it('closes dialog when cancel is clicked', async () => {
      const { openDialog } = setup()

      await openDialog()

      await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })

    it('closes dialog when confirm is clicked', async () => {
      const { openDialog } = setup()

      await openDialog()

      await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
  })

  describe('confirmation behaviour', () => {
    it('calls onConfirm when user confirms', async () => {
      const { openDialog, onConfirm } = setup()

      await openDialog()

      await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

      expect(onConfirm).toHaveBeenCalledTimes(1)
    })
  })
})
