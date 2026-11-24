import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  RadioButtonGroup,
  type RadioButtonGroupProps,
} from './RadioButtonGroup'

const options: RadioButtonGroupProps['options'] = [
  {
    label: 'Option 1',
    description: 'Description 1',
    value: '1',
  },
  {
    label: 'Option 2',
    description: 'Description 2',
    value: '2',
  },
  {
    label: 'Option 3',
    description: 'Description 3',
    value: '3',
  },
]

describe('<RadioButtonGroup />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group"
        options={options}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the label and radio buttons', () => {
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group"
        options={options}
      />
    )

    const radioGroup = screen.getByRole('group', {
      name: 'Radio Button Group',
    })
    expect(radioGroup).toBeInTheDocument()
    options.forEach((option) => {
      const radio = screen.getByRole('radio', { name: option.label })
      expect(radio).toBeInTheDocument()
    })
  })

  it('renders the description for each option in DETAILED variant', () => {
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Detailed Radio Button Group"
        variant="detailed"
        options={options}
      />
    )

    options.forEach((option) => {
      const radioDescription = screen.getByText(option.description as string)
      expect(radioDescription).toBeInTheDocument()
    })
  })

  it('handles disabled state', () => {
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Disabled Radio Button Group"
        options={options}
        disabled
      />
    )
    options.forEach((option) => {
      const radio = screen.getByRole('radio', { name: option.label })
      expect(radio).toBeDisabled()
    })
  })

  it('handles error state', () => {
    const errorMessage = 'This is an error message'
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group with Error"
        options={options}
        error={errorMessage}
      />
    )
    const errorAlert = screen.getByRole('alert')
    expect(errorAlert).toHaveTextContent(errorMessage)
    const group = screen.getByRole('group', {
      name: 'Radio Button Group with Error',
    })
    expect(group).toHaveAttribute('aria-invalid', 'true')
  })

  it('calls onChange when an option is selected', () => {
    const handleChange = vi.fn()
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group"
        options={options}
        onChange={handleChange}
      />
    )

    const radio = screen.getByRole('radio', { name: options[0].label })
    radio.click()

    expect(handleChange).toHaveBeenCalled()
  })

  it('sets one option as selected by default when initial value is provided', () => {
    render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group with Initial Value"
        options={options}
        onChange={() => {}}
        checkedOption={options[1].value}
      />
    )

    const selectedRadio = screen.getByRole('radio', {
      name: options[1].label,
    })
    expect(selectedRadio).toBeChecked()
  })

  describe('sizing', () => {
    it('forwards "fill" sizing to each radio button by default', () => {
      render(
        <RadioButtonGroup
          name="radio-button-group"
          label="Radio Button Group"
          options={options}
        />
      )

      const radios = screen.getAllByRole('radio')
      const optionsContainer = radios[0].closest('.radio-button-group-options')
      expect(optionsContainer).toHaveClass('sizing-fill')

      radios.forEach((radio) => {
        expect(radio.closest('.radio-button')).toHaveClass('sizing-fill')
      })
    })

    it('forwards "hug" sizing to each radio button', () => {
      render(
        <RadioButtonGroup
          name="radio-button-group"
          label="Radio Button Group"
          sizing="hug"
          options={options}
        />
      )

      const radios = screen.getAllByRole('radio')
      const optionsContainer = radios[0].closest('.radio-button-group-options')
      expect(optionsContainer).toHaveClass('sizing-hug')

      radios.forEach((radio) => {
        expect(radio.closest('.radio-button')).not.toHaveClass('sizing-fill')
      })
    })
  })

  describe('grid display', () => {
    it('applies the grid layout to the options container and makes each radio button fill its cell', () => {
      render(
        <RadioButtonGroup
          name="radio-button-group"
          label="Grid Radio Button Group"
          variant="detailed"
          display="grid"
          options={options}
        />
      )

      const radios = screen.getAllByRole('radio')
      const optionsContainer = radios[0].closest('.radio-button-group-options')
      expect(optionsContainer).toHaveClass('display-grid')
      expect(optionsContainer).not.toHaveClass('display-vertical')

      radios.forEach((radio) => {
        expect(radio.closest('.radio-button')).toHaveClass('sizing-fill')
      })
    })

    it('should render without accessibility violations', async () => {
      const { container } = render(
        <RadioButtonGroup
          name="radio-button-group"
          label="Grid Radio Button Group"
          variant="detailed"
          display="grid"
          options={options}
        />
      )

      expect(await axe(container)).toHaveNoViolations()
    })
  })

  it('should render an error message when options have duplicate values', () => {
    // `invokeGuardedCallbackDev` writes to stderr. This prevent useless noise in test results.
    const _stderrWriteSpy = vi
      .spyOn(process.stderr, 'write')
      .mockImplementation(vi.fn())
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    expect(() =>
      render(
        <RadioButtonGroup
          name="radio-button-group"
          label="Radio Button Group with Duplicate Values"
          options={[
            { label: 'Option 1', value: '1' },
            { label: 'Option 2', value: '1' },
          ]}
        />
      )
    ).toThrow('RadioButtonGroup options must have unique values.')
  })
})
