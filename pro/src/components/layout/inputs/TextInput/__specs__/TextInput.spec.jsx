import '@testing-library/jest-dom'

import { fireEvent } from '@testing-library/dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import TextInput from '../TextInput'

describe('src | components | layout | form | TextInput', () => {
  let props
  beforeEach(() => {
    props = {
      label: 'Label du champ',
      name: 'text-input',
      onChange: jest.fn(),
      placeholder: 'My placeholder',
      required: true,
      type: 'text',
      value: 'Some value',
    }
  })

  it('should display a text input with the provided value', () => {
    // when
    render(<TextInput {...props} />)

    // then
    expect(screen.getByLabelText(props.label)).toBeInTheDocument()
    expect(screen.getByLabelText(props.label)).toHaveAttribute(
      'value',
      props.value
    )
  })

  it('should call onChange function when value changes', async () => {
    // given
    render(<TextInput {...props} />)
    const offerTypeInput = await screen.findByLabelText(props.label)
    const newValue = 'My new value'

    // when
    fireEvent.change(offerTypeInput, { target: { value: newValue } })

    // then
    expect(props.onChange).toHaveBeenCalledTimes(1)
  })

  it('should not display a length count when input has only a max length', () => {
    // given
    props.maxLength = 20

    // when
    render(<TextInput {...props} />)

    // then
    expect(
      screen.queryByText(`${props.value.length}/${props.maxLength}`)
    ).not.toBeInTheDocument()
  })

  it('should display remainging characters when input has a max length and ask character count', () => {
    // given
    props.maxLength = 20
    props.countCharacters = true

    // when
    render(<TextInput {...props} />)

    // then
    expect(
      screen.getByText(`${props.value.length}/${props.maxLength}`)
    ).toBeInTheDocument()
  })
})
