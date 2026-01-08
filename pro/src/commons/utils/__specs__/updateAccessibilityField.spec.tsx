import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { useState } from 'react'

import type { AccessibilityFormValues } from '@/commons/core/shared/types'
import { CheckboxGroup } from '@/design-system/CheckboxGroup/CheckboxGroup'

import type { Nullable } from '../types'
import {
  type SetAccessibilityFieldValue,
  updateAccessibilityField,
} from '../updateAccessibilityField'

const mockSetFieldValue = vi.fn()

function TestCheckboxGroup() {
  const [formValues, setFormValues] = useState<{
    accessibility: Nullable<AccessibilityFormValues> | undefined
  }>({ accessibility: undefined })

  const setFieldValue: SetAccessibilityFieldValue = (
    name,
    nextValue,
    options
  ) => {
    expect(name).toBe('accessibility')
    assert(typeof nextValue !== 'boolean')

    setFormValues({ accessibility: nextValue ?? undefined })
    mockSetFieldValue(name, nextValue, options)
  }

  const options = updateAccessibilityField(
    setFieldValue,
    formValues.accessibility
  )

  return <CheckboxGroup options={options} label="accessibility" />
}

const renderUseAccessibilityOptions = () => {
  return render(<TestCheckboxGroup />)
}

describe('updateAccessibilityField', () => {
  beforeEach(() => {
    mockSetFieldValue.mockClear()
  })

  it('should return default options when accessibilityValues is undefined', () => {
    const result = updateAccessibilityField(mockSetFieldValue, undefined)

    expect(mockSetFieldValue).not.toHaveBeenCalled()
    expect(result).toMatchObject([
      {
        checked: false,
        label: 'Visuel',
      },
      {
        checked: false,
        label: 'Psychique ou cognitif',
      },
      {
        checked: false,
        label: 'Moteur',
      },
      {
        checked: false,
        label: 'Auditif',
      },
      {
        checked: false,
        label: 'Non accessible',
      },
    ])
  })

  it('should handle toggling visual option updating root object', async () => {
    renderUseAccessibilityOptions()

    const visualCheckbox = screen.getByRole('checkbox', { name: 'Visuel' })

    await userEvent.click(visualCheckbox) // check "Visuel"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(1)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      1,
      'accessibility',
      {
        none: false,
        visual: true,
        mental: false,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )

    await userEvent.click(visualCheckbox) // uncheck "Visuel"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(2)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      2,
      'accessibility',
      {
        none: false,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )
  })

  it('should handle mental and motor option changes updating root object', async () => {
    renderUseAccessibilityOptions()

    const mentalCheckbox = screen.getByRole('checkbox', {
      name: 'Psychique ou cognitif',
    })

    await userEvent.click(mentalCheckbox) // check "Psychique ou cognitif"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(1)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      1,
      'accessibility',
      {
        none: false,
        visual: false,
        mental: true,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )

    await userEvent.click(mentalCheckbox) // uncheck "Psychique ou cognitif"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(2)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      2,
      'accessibility',
      {
        none: false,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )

    const motorCheckbox = screen.getByRole('checkbox', {
      name: 'Moteur',
    })
    await userEvent.click(motorCheckbox) // check "Moteur"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(3)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      3,
      'accessibility',
      {
        none: false,
        visual: false,
        mental: false,
        motor: true,
        audio: false,
      },
      { shouldValidate: true }
    )
  })

  it('should unset none flag when another option is checked', async () => {
    renderUseAccessibilityOptions()

    const audioCheckbox = screen.getByRole('checkbox', {
      name: 'Auditif',
    })

    await userEvent.click(audioCheckbox)

    expect(mockSetFieldValue).toHaveBeenCalledTimes(1)
    expect(mockSetFieldValue).toHaveBeenCalledWith(
      'accessibility',
      {
        none: false,
        visual: false,
        mental: false,
        motor: false,
        audio: true,
      },
      { shouldValidate: true }
    )
  })

  it('should toggle none option updating entire object', async () => {
    renderUseAccessibilityOptions()

    const noneCheckbox = screen.getByRole('checkbox', {
      name: 'Non accessible',
    })
    await userEvent.click(noneCheckbox) // check "Non accessible"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(1)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      1,
      'accessibility',
      {
        none: true,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )

    await userEvent.click(noneCheckbox) // uncheck "Non accessible"

    expect(mockSetFieldValue).toHaveBeenCalledTimes(2)
    expect(mockSetFieldValue).toHaveBeenNthCalledWith(
      2,
      'accessibility',
      {
        none: false,
        visual: false,
        mental: false,
        motor: false,
        audio: false,
      },
      { shouldValidate: true }
    )
  })
})
