import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { Button } from '@/design-system/Button/Button'

import { DropdownButton, type DropdownButtonProps } from './DropdownButton'

const defaultProps: DropdownButtonProps = {
  name: 'Trigger',
  options: [
    { id: '1', element: <Button label="Button 1" onClick={() => {}}></Button> },
    {
      id: '2',
      element: <Button label="Button 2" onClick={() => {}}></Button>,
    },
  ],
}

function renderDropdownButton(props?: Partial<DropdownButtonProps>) {
  return render(
    <>
      <DropdownButton {...defaultProps} {...props} />
      <span>Other element</span>
    </>
  )
}

describe('DropdownButton', () => {
  it('should not have any accessibility violation', async () => {
    const { container } = renderDropdownButton()
    expect(await axe(container)).toHaveNoViolations()

    await userEvent.click(screen.getByRole('button', { name: 'Trigger' }))

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should open the dropdown when the trigger is clicked', async () => {
    renderDropdownButton()

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
    renderDropdownButton()

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
