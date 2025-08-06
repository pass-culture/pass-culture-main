import { render, screen, waitFor } from '@testing-library/react'
import { axe } from 'vitest-axe'

import {
  RadioButtonSizing,
  RadioButtonVariantProps,
} from '@/design-system/RadioButton/RadioButton'

import { RadioButtonGroup, RadioButtonGroupProps } from './RadioButtonGroup'

const options: RadioButtonGroupProps<
  string,
  RadioButtonVariantProps,
  RadioButtonSizing,
  boolean,
  (event: React.ChangeEvent<HTMLInputElement>) => void,
  (event: React.FocusEvent<HTMLInputElement>) => void
>['options'] = [
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

    const radioGroup = screen.getByRole('radiogroup', {
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
    options.forEach((option) => {
      const radio = screen.getByRole('radio', { name: option.label })
      expect(radio).toHaveAttribute('aria-invalid', 'true')
    })
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

  it('should render an error message when less than 2 options are provided', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => vi.fn())
    await waitFor(() =>
      expect(() =>
        render(
          <RadioButtonGroup
            name="radio-button-group"
            label="Radio Button Group with Insufficient Options"
            options={[options[0]]}
          />
        )
      ).toThrow('RadioButtonGroup requires at least two options.')
    )
    vi.restoreAllMocks()
  })

  it('should not render an error when less than 2 options are provided but allowSingleOrNoneOption prop is passed', () => {
    const { container } = render(
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group with Insufficient Options & allowSingleOrNoneOption"
        options={[options[0]]}
        allowSingleOrNoneOption
      />
    )

    expect(container).toBeInTheDocument()
  })

  it('should render an error message when options have duplicate values', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => vi.fn())
    await waitFor(() =>
      expect(() =>
        render(
          <RadioButtonGroup
            name="radio-button-group"
            label="Radio Button Group with Duplicate Values"
            options={[
              { label: 'Option 1', value: '1' },
              { label: 'Option 2', value: '1' }, // Duplicate value
            ]}
          />
        )
      ).toThrow('RadioButtonGroup options must have unique values.')
    )
    vi.restoreAllMocks()
  })
})
