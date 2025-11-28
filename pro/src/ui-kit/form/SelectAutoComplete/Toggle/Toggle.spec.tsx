import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Toggle, type ToggleProps } from './Toggle'

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
      fieldName: 'name',
    })

    expect(screen.getByRole('button')).toHaveAttribute(
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
      fieldName: 'name',
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
      fieldName: 'name',
    })

    expect(screen.getByRole('button')).toHaveAttribute(
      'aria-label',
      'Masquer les options'
    )
  })
})
