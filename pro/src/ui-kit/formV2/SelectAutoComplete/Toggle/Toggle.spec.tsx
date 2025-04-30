import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { Toggle, ToggleProps } from './Toggle'

const renderToggle = (
  props: ToggleProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<Toggle {...props} />, { ...options })
}

describe('<Toggle />', () => {
  it('should call "toggleField" on click if button is not disabled', async () => {
    const toggleField = vi.fn()

    renderToggle({
      disabled: false,
      isOpen: false,
      toggleField,
    })

    expect(screen.getByRole('button').querySelector('svg')).toHaveAttribute(
      'aria-label',
      'Afficher les options'
    )

    const user = userEvent.setup()

    await user.click(screen.getByRole('button'))

    expect(toggleField).toHaveBeenCalledOnce()
  })

  it('should not call "toggleField" on click if button is disabled', async () => {
    const toggleField = vi.fn()

    renderToggle({
      disabled: true,
      isOpen: false,
      toggleField,
    })

    const user = userEvent.setup()

    await user.click(screen.getByRole('button'))

    expect(toggleField).not.toHaveBeenCalled()
  })

  it('should be opened if "isOpen" is true', () => {
    renderToggle({
      disabled: false,
      isOpen: true,
      toggleField: vi.fn(),
    })

    expect(screen.getByRole('button').querySelector('svg')).toHaveAttribute(
      'aria-label',
      'Masquer les options'
    )
  })
})
