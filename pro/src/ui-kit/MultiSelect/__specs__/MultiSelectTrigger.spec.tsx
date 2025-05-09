import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { MultiSelectTrigger } from '../MultiSelectTrigger'

describe('<MultiSelectTrigger />', () => {
  const mockToggleDropdown = vi.fn()

  const renderMultiSelectPanel = ({
    disabled = false,
    isOpen = false,
    selectedCount = 0,
  }: {
    disabled?: boolean
    isOpen?: boolean
    selectedCount?: number
  } = {}) => {
    return render(
      <MultiSelectTrigger
        id="1"
        toggleDropdown={mockToggleDropdown}
        buttonLabel={'Options Label'}
        disabled={disabled}
        isOpen={isOpen}
        selectedCount={selectedCount}
      />
    )
  }

  it('should render correctly', () => {
    renderMultiSelectPanel({ selectedCount: 2 })

    expect(screen.getByText('Options Label')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('should have no accessibility violations', async () => {
    const { container } = renderMultiSelectPanel()

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should disable the button when disabled prop is passed', () => {
    renderMultiSelectPanel({ disabled: true })

    const button = screen.getByRole('button')

    expect(button).toBeDisabled()
  })

  it('should display the chevron open icon if panel is opened', () => {
    const { container } = renderMultiSelectPanel({
      disabled: true,
      isOpen: true,
    })

    let chevronIcon = container.querySelector('svg')

    expect(chevronIcon).toHaveClass('chevron chevronOpen')
  })

  it('should not display the chevron icon open if panel is closed', () => {
    const { container } = renderMultiSelectPanel()

    let chevronIcon = container.querySelector('svg')

    chevronIcon = container.querySelector('svg')

    expect(chevronIcon).not.toHaveClass('chevron chevronOpen')
  })

  it('should render badge with correct count when options are selected', () => {
    renderMultiSelectPanel({ selectedCount: 3 })

    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('should not render badge when no options are selected', () => {
    renderMultiSelectPanel({ selectedCount: 0 })

    const badge = screen.queryByText('0')
    expect(badge).toBeNull()
  })

  it('should update badge count when selecting and deselecting options', () => {
    const { rerender } = renderMultiSelectPanel({ selectedCount: 2 })

    expect(screen.getByText('2')).toBeInTheDocument()

    rerender(5)

    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('should call toggleDropdown when the button is clicked', async () => {
    renderMultiSelectPanel()

    const button = screen.getByRole('button')

    await userEvent.click(button)

    expect(mockToggleDropdown).toHaveBeenCalledTimes(1)
  })
})
