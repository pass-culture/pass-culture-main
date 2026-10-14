import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe } from 'vitest'
import { axe } from 'vitest-axe'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ToggleButtonGroup,
  type ToggleButtonGroupProps,
} from './ToggleButtonGroup'

const mockLeftClick = vi.fn()
const mockRightClick = vi.fn()
const defaultProps: ToggleButtonGroupProps = {
  left: {
    id: 'left',
    label: 'left',
    icon: undefined,
    iconAlt: undefined,
    selected: undefined,
    handleClick: mockLeftClick,
  },
  right: {
    id: 'right',
    label: 'right',
    icon: undefined,
    iconAlt: undefined,
    selected: undefined,
    handleClick: mockRightClick,
  },
  selected: 'left',
  controls: 'form',
}

const render = (props: ToggleButtonGroupProps = defaultProps) =>
  renderWithProviders(
    <>
      <div id="form"></div>
      <ToggleButtonGroup {...props} />
    </>,
    {
      user: sharedCurrentUserFactory(),
    }
  )

describe('ToggleButtonGroup', () => {
  it('should render', async () => {
    const { container } = render()

    expect(await axe(container)).toHaveNoViolations()
    expect(screen.getByRole('tab', { name: 'left' })).toHaveProperty(
      'ariaSelected',
      'true'
    )
  })

  it('should select right button', () => {
    render({ ...defaultProps, selected: 'right' })

    expect(screen.getByRole('tab', { name: 'left' })).toHaveProperty(
      'ariaSelected',
      'false'
    )
    expect(screen.getByRole('tab', { name: 'right' })).toHaveProperty(
      'ariaSelected',
      'true'
    )
  })

  it('should call on click', async () => {
    render()

    // Should not call if the button is already pressed
    await userEvent.click(screen.getByRole('tab', { name: 'left' }))
    expect(mockLeftClick).not.toHaveBeenCalled()

    await userEvent.click(screen.getByRole('tab', { name: 'right' }))
    await waitFor(() => {
      expect(mockRightClick).toHaveBeenCalled()
      expect(screen.getByRole('tab', { name: 'right' })).toHaveProperty(
        'ariaSelected',
        'true'
      )
    })
    await userEvent.click(screen.getByRole('tab', { name: 'left' }))
    await waitFor(() => {
      expect(mockLeftClick).toHaveBeenCalled()
      expect(screen.getByRole('tab', { name: 'left' })).toHaveProperty(
        'ariaSelected',
        'true'
      )
    })
  })

  it('should have working keyboard navigation', async () => {
    render()

    await userEvent.click(screen.getByRole('tab', { name: 'left' }))

    await userEvent.keyboard('{ArrowLeft}')
    expect(screen.getByRole('tab', { name: 'left' })).toHaveProperty(
      'ariaSelected',
      'true'
    )
    expect(screen.getByRole('tab', { name: 'right' })).toHaveProperty(
      'ariaSelected',
      'false'
    )
    await userEvent.keyboard('{ArrowRight}')
    await waitFor(() => {
      expect(screen.getByRole('tab', { name: 'right' })).toHaveProperty(
        'ariaSelected',
        'true'
      )
      expect(screen.getByRole('tab', { name: 'left' })).toHaveProperty(
        'ariaSelected',
        'false'
      )
    })
  })
})
