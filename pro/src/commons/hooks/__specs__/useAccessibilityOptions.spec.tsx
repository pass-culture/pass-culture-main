import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { AccessibilityFormValues } from 'commons/core/shared/types'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'

import { useAccessibilityOptions } from '../useAccessibilityOptions'

const mockSetFieldValue = vi.fn()

function TestCheckboxGroup() {
  const group = useAccessibilityOptions(
    mockSetFieldValue,
    {} as AccessibilityFormValues
  )

  return (
    <CheckboxGroup group={group} name="accessibility" legend="accessibility" />
  )
}

const renderUseAccessibilityOptions = () => {
  return render(<TestCheckboxGroup />)
}

describe('useAccessibilityOptions', () => {
  it('should uncheck all options if none is clicked', async () => {
    renderUseAccessibilityOptions()
    const noneCheckbock = screen.getByRole('checkbox', {
      name: 'Non accessible',
    })
    await userEvent.click(noneCheckbock)
    expect(mockSetFieldValue).toHaveBeenCalledWith('accessibility', {
      none: true,
      visual: false,
      mental: false,
      motor: false,
      audio: false,
    })
  })

  it('should uncheck none option if any other is clicked', async () => {
    renderUseAccessibilityOptions()
    const audioCheckbox = screen.getByRole('checkbox', {
      name: 'Auditif',
    })
    await userEvent.click(audioCheckbox)
    expect(mockSetFieldValue).toHaveBeenCalledWith('accessibility.none', false)
    expect(mockSetFieldValue).toHaveBeenCalledWith('accessibility.audio', true)
  })

  it('should only uncheck none option when unchecking it', async () => {
    renderUseAccessibilityOptions()
    const noneCheckbox = screen.getByRole('checkbox', {
      name: 'Non accessible',
    })
    await userEvent.click(noneCheckbox)
    await userEvent.click(noneCheckbox)
    expect(mockSetFieldValue).toHaveBeenCalledTimes(2)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(2, 'accessibility', {
      none: true,
      visual: false,
      mental: false,
      motor: false,
      audio: false,
    })
  })
})
