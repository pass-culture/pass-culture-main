import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { ButtonInvalidateToken } from '..'

describe('ButtonInvalidateToken', () => {
  it('should open modal on invalidate button click', async () => {
    render(<ButtonInvalidateToken onConfirm={vi.fn()} />)

    await userEvent.click(screen.getByText('Invalider la contremarque'))

    expect(
      screen.getByText('Voulez-vous vraiment invalider cette contremarque ?')
    ).toBeInTheDocument()
  })

  it('should close Dialog on cancel button click', async () => {
    render(<ButtonInvalidateToken onConfirm={vi.fn()} />)

    await userEvent.click(screen.getByText('Invalider la contremarque'))
    await userEvent.click(screen.getByText('Annuler'))

    expect(
      screen.queryByText('Voulez-vous vraiment invalider cette contremarque ?')
    ).not.toBeInTheDocument()
  })

  it('should close Dialog on confirm button click', async () => {
    render(<ButtonInvalidateToken onConfirm={vi.fn()} />)

    await userEvent.click(screen.getByText('Invalider la contremarque'))
    await userEvent.click(screen.getByText('Continuer'))

    expect(
      screen.queryByText('Voulez-vous vraiment invalider cette contremarque ?')
    ).not.toBeInTheDocument()
  })
})
