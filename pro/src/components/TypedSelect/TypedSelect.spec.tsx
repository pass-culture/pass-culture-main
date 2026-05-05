import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { EMPTY_OPTION_VALUE } from './constants'
import { TypedSelect } from './TypedSelect'

const stringOptions = [
  { label: 'Option A', value: 'a' },
  { label: 'Option B', value: 'b' },
]

const numberOptions = [
  { label: 'One', value: 1 },
  { label: 'Two', value: 2 },
]

describe('TypedSelect', () => {
  it('should render the select with its label', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        options={stringOptions}
        value={undefined}
        onChange={vi.fn()}
      />
    )

    expect(screen.getByLabelText('My label')).toBeInTheDocument()
  })

  it('should render all provided options', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        options={stringOptions}
        value={undefined}
        onChange={vi.fn()}
      />
    )

    expect(screen.getByRole('option', { name: 'Option A' })).toBeInTheDocument()
    expect(screen.getByRole('option', { name: 'Option B' })).toBeInTheDocument()
  })

  it('should render the empty option when emptyOptionLabel is provided', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        emptyOptionLabel="All"
        options={stringOptions}
        value={undefined}
        onChange={vi.fn()}
      />
    )

    const emptyOption = screen.getByRole<HTMLOptionElement>('option', {
      name: 'All',
    })
    expect(emptyOption).toBeInTheDocument()
    expect(emptyOption.value).toBe(EMPTY_OPTION_VALUE)
  })

  it('should not render the empty option when emptyOptionLabel is not provided', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        options={stringOptions}
        value={undefined}
        onChange={vi.fn()}
      />
    )

    expect(
      screen.queryByRole('option', { name: 'All' })
    ).not.toBeInTheDocument()
  })

  it('should select the empty option when value is undefined', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        emptyOptionLabel="All"
        options={stringOptions}
        value={undefined}
        onChange={vi.fn()}
      />
    )

    expect(screen.getByLabelText<HTMLSelectElement>('My label').value).toBe(
      EMPTY_OPTION_VALUE
    )
  })

  it('should select the matching option when value is a string', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        options={stringOptions}
        value="b"
        onChange={vi.fn()}
      />
    )

    expect(screen.getByLabelText<HTMLSelectElement>('My label').value).toBe('b')
  })

  it('should select the matching option when value is a number', () => {
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        isNumber
        options={numberOptions}
        value={2}
        onChange={vi.fn()}
      />
    )

    expect(screen.getByLabelText<HTMLSelectElement>('My label').value).toBe('2')
  })

  it('should call onChange with the string value when a string option is selected', async () => {
    const onChange = vi.fn()
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        options={stringOptions}
        value={undefined}
        onChange={onChange}
      />
    )

    await userEvent.selectOptions(screen.getByLabelText('My label'), 'a')

    expect(onChange).toHaveBeenCalledWith('a')
  })

  it('should call onChange with a number when isNumber is true and a number option is selected', async () => {
    const onChange = vi.fn()
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        isNumber
        options={numberOptions}
        value={undefined}
        onChange={onChange}
      />
    )

    await userEvent.selectOptions(screen.getByLabelText('My label'), '1')

    expect(onChange).toHaveBeenCalledWith(1)
    expect(typeof onChange.mock.calls[0][0]).toBe('number')
  })

  it('should call onChange with undefined when the empty option is selected', async () => {
    const onChange = vi.fn()
    render(
      <TypedSelect
        label="My label"
        name="mySelect"
        emptyOptionLabel="All"
        options={stringOptions}
        value="a"
        onChange={onChange}
      />
    )

    await userEvent.selectOptions(screen.getByLabelText('My label'), 'All')

    expect(onChange).toHaveBeenCalledWith(undefined)
  })
})
