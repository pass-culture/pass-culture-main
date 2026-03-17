import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { UseFormRegisterReturn } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { AddressFields } from './AddressFields'

vi.mock('@/ui-kit/form/AddressSelect/AddressSelect', () => ({
  AddressSelect: (props: any) => (
    <div data-disabled={props.disabled}>AddressSelect</div>
  ),
}))

describe('<AddressFields />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <AddressFields
        addressRegister={
          { name: 'location' } as unknown as UseFormRegisterReturn
        }
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('toggles manual mode when button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <AddressFields
        addressRegister={{ name: 'location' } as any}
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    expect(screen.queryByText('Manual')).not.toBeInTheDocument()

    await user.click(
      screen.getByRole('button', {
        name: /Vous ne trouvez pas votre adresse/,
      })
    )

    expect(screen.getByText('Manual')).toBeInTheDocument()

    expect(screen.getByText('AddressSelect')).toHaveAttribute(
      'data-disabled',
      'true'
    )
  })

  it('changes button label when switching modes', async () => {
    const user = userEvent.setup()

    render(
      <AddressFields
        addressRegister={{ name: 'location' } as any}
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    await user.click(screen.getByRole('button'))

    expect(
      screen.getByRole('button', {
        name: 'Revenir à la sélection automatique',
      })
    ).toBeInTheDocument()
  })

  it('uses controlled manual prop', () => {
    render(
      <AddressFields
        manual
        addressRegister={{ name: 'location' } as any}
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    expect(screen.getByText('Manual')).toBeInTheDocument()
  })

  it('calls onManualChange when toggled', async () => {
    const user = userEvent.setup()
    const onManualChange = vi.fn()

    render(
      <AddressFields
        manual={false}
        onManualChange={onManualChange}
        addressRegister={{ name: 'location' } as any}
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    await user.click(screen.getByRole('button'))

    expect(onManualChange).toHaveBeenCalledWith(true)
  })

  it('does not toggle when disabled', async () => {
    const user = userEvent.setup()

    render(
      <AddressFields
        disabled
        addressRegister={{ name: 'location' } as any}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    await user.click(screen.getByRole('button'))

    expect(screen.queryByText('Manual')).not.toBeInTheDocument()
  })

  it('hides error when manual mode is active', async () => {
    const user = userEvent.setup()

    render(
      <AddressFields
        error="Error message"
        addressRegister={{ name: 'location' } as any}
        disabled={false}
        renderManual={() => <span>Manual</span>}
        onAddressChosen={() => {}}
      />
    )

    await user.click(screen.getByRole('button'))

    expect(screen.queryByText('Error message')).not.toBeInTheDocument()
  })
})
