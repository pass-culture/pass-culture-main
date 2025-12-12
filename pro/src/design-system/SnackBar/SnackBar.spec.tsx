import { act, render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { SnackBar, type SnackBarProps, SnackBarVariant } from './SnackBar'

const renderSnackBar = (props: SnackBarProps) => {
  return render(<SnackBar {...props} />)
}

const mockOnClose = vi.fn()

const defaultProps: SnackBarProps = {
  text: 'Message de test',
  variant: SnackBarVariant.SUCCESS,
  autoClose: false,
  onClose: mockOnClose,
}

describe('SnackBar', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mockOnClose.mockClear()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should have an accessible structure', async () => {
    vi.useRealTimers()
    const { container } = renderSnackBar({
      ...defaultProps,
      autoClose: false,
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the text and the close button', () => {
    renderSnackBar(defaultProps)

    expect(screen.getByText('Message de test')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Fermer le message' })
    ).toBeInTheDocument()
  })

  it('should have role="status" and aria-live="polite" for success variant', () => {
    renderSnackBar({
      ...defaultProps,
      variant: SnackBarVariant.SUCCESS,
      testId: 'snackbar',
    })

    const snackbar = screen.getByTestId('snackbar')
    expect(snackbar).toHaveAttribute('role', 'status')
    expect(snackbar).toHaveAttribute('aria-live', 'polite')
  })

  it('should have role="alert" and aria-live="assertive" for error variant', () => {
    renderSnackBar({
      ...defaultProps,
      variant: SnackBarVariant.ERROR,
      testId: 'snackbar',
    })

    const snackbar = screen.getByTestId('snackbar')
    expect(snackbar).toHaveAttribute('role', 'alert')
    expect(snackbar).toHaveAttribute('aria-live', 'assertive')
  })

  it('should call onClose when close button is clicked after animation', async () => {
    vi.useRealTimers()
    renderSnackBar(defaultProps)

    const closeButton = screen.getByRole('button', {
      name: 'Fermer le message',
    })
    await userEvent.click(closeButton)

    // onClose est appelé après l'animation (300ms)
    await waitFor(
      () => {
        expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
      },
      { timeout: 500 }
    )
  })

  it('should auto-close after 5 seconds for short text', () => {
    renderSnackBar({
      ...defaultProps,
      text: 'Court message',
      autoClose: true,
    })

    expect(defaultProps.onClose).not.toHaveBeenCalled()

    // Avancer de 5 secondes (durée pour texte court)
    act(() => {
      vi.advanceTimersByTime(5000)
    })

    // Puis attendre l'animation de fermeture (300ms)
    act(() => {
      vi.advanceTimersByTime(300)
    })

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('should auto-close after 10 seconds for long text (> 120 characters)', () => {
    const longText =
      'Ceci est un message très long qui dépasse les 120 caractères pour tester que la durée de fermeture automatique est bien de 10 secondes'
    renderSnackBar({
      ...defaultProps,
      text: longText,
      autoClose: true,
    })

    expect(longText.length).toBeGreaterThan(120)

    // Après 5 secondes, ne devrait pas encore être fermé
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(defaultProps.onClose).not.toHaveBeenCalled()

    // Après 10 secondes + animation
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    act(() => {
      vi.advanceTimersByTime(300)
    })

    expect(defaultProps.onClose).toHaveBeenCalledTimes(1)
  })

  it('should not auto-close when autoClose is false', () => {
    renderSnackBar(defaultProps)

    act(() => {
      vi.advanceTimersByTime(10000)
    })

    expect(defaultProps.onClose).not.toHaveBeenCalled()
  })

  it('should have show class when rendered', () => {
    renderSnackBar({
      ...defaultProps,
      testId: 'snackbar',
    })

    const snackbar = screen.getByTestId('snackbar')
    expect(snackbar).toHaveClass('show')
  })
})
