import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { Button } from '@/design-system/Button/Button'

import { Dropdown, type DropdownProps } from './Dropdown'
import { DropdownItem } from './DropdownItem'

const defaultProps: DropdownProps = {
  title: 'dropdown',
  trigger: <Button label="Trigger" onClick={() => {}}></Button>,
}

function renderDropdown(props?: Partial<DropdownProps>) {
  return render(
    <>
      <Dropdown {...defaultProps} {...props}>
        <DropdownItem>
          <Button label="Button 1" onClick={() => {}}></Button>
        </DropdownItem>
        <DropdownItem>
          <Button label="Button 2" onClick={() => {}}></Button>
        </DropdownItem>
      </Dropdown>
      <span>Other element</span>
    </>
  )
}

describe('Dropdown', () => {
  it('should not have any accessibility violation', async () => {
    const { container } = renderDropdown()
    expect(await axe(container)).toHaveNoViolations()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should open the dropdown when the trigger is clicked', async () => {
    renderDropdown()

    const trigger = screen.getByRole('button', { name: 'Trigger' })

    expect(trigger).toBeInTheDocument()

    expect(
      screen.queryByRole('menuitem', { name: 'Button 1' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('menuitem', { name: 'Button 2' })
    ).not.toBeInTheDocument()

    await userEvent.click(trigger)

    expect(
      screen.getByRole('menuitem', { name: 'Button 1' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('menuitem', { name: 'Button 2' })
    ).toBeInTheDocument()
  })

  it('should close the dropdown menu when the user clicks outside', async () => {
    renderDropdown()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    expect(
      screen.getByRole('menuitem', { name: 'Button 1' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('menuitem', { name: 'Button 2' })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Other element'), {
      pointerEventsCheck: 0,
    })

    expect(
      screen.queryByRole('menuitem', { name: 'Button 1' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('menuitem', { name: 'Button 2' })
    ).not.toBeInTheDocument()
  })
})
