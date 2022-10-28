import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import Select from '../Select'

describe('src | components | layout | form | Select', () => {
  let props
  beforeEach(() => {
    props = {
      defaultOption: { displayName: 'Option par défaut', id: 'all' },
      handleSelection: jest.fn(),
      isDisabled: false,
      label: 'Label de mon select',
      name: 'items-select',
      options: [
        { displayName: 'Ma première option', id: '1' },
        { displayName: 'Ma deuxième option', id: '2' },
      ],
      selectedValue: 'all',
    }
  })

  it('should render a select input with the provided default value', async () => {
    // given
    props.options = []

    // when
    render(<Select {...props} />)

    // then
    const option = screen.getByRole('option')
    expect(option).toHaveTextContent(props.defaultOption.displayName)
  })

  it('should render a select input containing given options in given order', async () => {
    // when
    render(<Select {...props} />)

    // then
    const options = screen.getAllByRole('option')
    expect(options).toHaveLength(3)
    expect(options[1]).toHaveTextContent(props.options[0].displayName)
    expect(options[2]).toHaveTextContent(props.options[1].displayName)
  })

  it('should have given option selected when value is given', async () => {
    // given
    props.selectedValue = props.options[0].id

    // when
    render(<Select {...props} />)

    // then
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue(props.options[0].id)
  })

  it('should call callback on blur', async () => {
    render(<Select {...props} />)
    const options = screen.getAllByRole('option')

    // when
    await userEvent.click(options[1])
    await userEvent.tab()

    // then
    expect(props.handleSelection).toHaveBeenCalledTimes(1)
  })

  it('should call callback on change', async () => {
    render(<Select {...props} />)

    const options = screen.getAllByRole('option')

    // when
    await userEvent.selectOptions(screen.getByRole('combobox'), options[0])

    // then
    expect(props.handleSelection).toHaveBeenCalledTimes(1)
  })
})
