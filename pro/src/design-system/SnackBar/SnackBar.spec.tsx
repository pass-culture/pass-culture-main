import { act, render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { SnackBar, type SnackBarProps, SnackBarVariant } from './SnackBar'

const renderSnackBar = (props: SnackBarProps) => {
  return render(<SnackBar {...props} />)
}

const defaultProps: SnackBarProps = {
  text: 'Message de test',
  variant: SnackBarVariant.SUCCESS,
  autoClose: false,
}

describe('SnackBar', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should have an accessible structure', async () => {
    vi.useRealTimers()
    const { container } = renderSnackBar({
      ...defaultProps,
      autoClose: false,
      isVisible: false, // Évite les animations/intervals
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
    const onClose = vi.fn()
    renderSnackBar({
      ...defaultProps,
      onClose,
    })

    const closeButton = screen.getByRole('button', {
      name: 'Fermer le message',
    })
    await userEvent.click(closeButton)

    // onClose est appelé après l'animation (300ms)
    await waitFor(
      () => {
        expect(onClose).toHaveBeenCalledTimes(1)
      },
      { timeout: 500 }
    )
  })

  it('should auto-close after 5 seconds for short text', () => {
    const onClose = vi.fn()
    renderSnackBar({
      text: 'Court message',
      variant: SnackBarVariant.SUCCESS,
      autoClose: true,
      onClose,
    })

    expect(onClose).not.toHaveBeenCalled()

    // Avancer de 5 secondes (durée pour texte court)
    act(() => {
      vi.advanceTimersByTime(5000)
    })

    // Puis attendre l'animation de fermeture (300ms)
    act(() => {
      vi.advanceTimersByTime(300)
    })

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('should auto-close after 10 seconds for long text (> 120 characters)', () => {
    const onClose = vi.fn()
    const longText =
      'Ceci est un message très long qui dépasse les 120 caractères pour tester que la durée de fermeture automatique est bien de 10 secondes'
    renderSnackBar({
      text: longText,
      variant: SnackBarVariant.SUCCESS,
      autoClose: true,
      onClose,
    })

    expect(longText.length).toBeGreaterThan(120)

    // Après 5 secondes, ne devrait pas encore être fermé
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    expect(onClose).not.toHaveBeenCalled()

    // Après 10 secondes + animation
    act(() => {
      vi.advanceTimersByTime(5000)
    })
    act(() => {
      vi.advanceTimersByTime(300)
    })

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('should not auto-close when autoClose is false', () => {
    const onClose = vi.fn()
    renderSnackBar({
      ...defaultProps,
      autoClose: false,
      onClose,
    })

    act(() => {
      vi.advanceTimersByTime(10000)
    })

    expect(onClose).not.toHaveBeenCalled()
  })

  it('should not be visible when isVisible is false', () => {
    renderSnackBar({
      ...defaultProps,
      isVisible: false,
      testId: 'snackbar',
    })

    const snackbar = screen.getByTestId('snackbar')
    // Le composant est rendu mais sans la classe 'show'
    expect(snackbar).not.toHaveClass('show')
  })

  it('should reset state when isVisible changes from false to true', () => {
    const { rerender } = renderSnackBar({
      ...defaultProps,
      isVisible: false,
      testId: 'snackbar',
    })

    rerender(<SnackBar {...defaultProps} isVisible={true} testId="snackbar" />)

    const snackbar = screen.getByTestId('snackbar')
    expect(snackbar).toHaveClass('show')
  })
})
