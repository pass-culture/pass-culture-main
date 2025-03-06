import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PHONE_EXAMPLE_MAP } from './constants'
import { PhoneNumberInput, PhoneNumberInputProps } from './PhoneNumberInput'

const renderPhoneNumberInput = ({
  label = 'Mon label',
  ...props
}: Partial<PhoneNumberInputProps>) => {
  render(
    <>
      <PhoneNumberInput name="phone" label={label} {...props} />
      <a href="#">Dummy element only here to receive the focus</a>
    </>
  )
}

describe('PhoneNumberInput', () => {
  it('should have by default the first prefix of the list PHONE_CODE_COUNTRY_CODE_OPTIONS and its corresponding placeholder', () => {
    renderPhoneNumberInput({})

    const defaultCountryCodeOption = PHONE_CODE_COUNTRY_CODE_OPTIONS[0]
    const defaultExample = PHONE_EXAMPLE_MAP[defaultCountryCodeOption.value]

    expect(defaultExample).toBeDefined()
    expect(screen.getByRole('combobox')).toHaveValue(
      defaultCountryCodeOption.value
    )
    expect(
      screen.getByText(`Par exemple : ${defaultExample}`)
    ).toBeInTheDocument()
  })

  it('should change the placeholder when user change country code', async () => {
    renderPhoneNumberInput({})
    const countryCodeSelect = screen.getByRole('combobox')

    await userEvent.selectOptions(countryCodeSelect, '+590')

    const guadeloupeExample = PHONE_EXAMPLE_MAP['+590']
    expect(guadeloupeExample).toBeDefined()
    expect(
      screen.getByText(`Par exemple : ${guadeloupeExample}`)
    ).toBeInTheDocument()
  })

  it('should show an error if prop "error" is set', () => {
    renderPhoneNumberInput({
      error:
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678',
    })
    expect(
      screen.queryByText(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
    ).toBeInTheDocument()
  })

  describe('should separate correctly phone values', () => {
    it.each([
      {
        value: '+33612345678',
        prefix: '+33',
        phoneNumber: '612345678',
      },
      {
        value: '+262692123456',
        prefix: '+262',
        phoneNumber: '692123456',
      },
      {
        value: '+508551234',
        prefix: '+508',
        phoneNumber: '551234',
      },
      {
        value: '+590690000102',
        prefix: '+590',
        phoneNumber: '690000102',
      },
      {
        value: '+594694000102',
        prefix: '+594',
        phoneNumber: '694000102',
      },
      {
        value: '+596696000102',
        prefix: '+596',
        phoneNumber: '696000102',
      },
      {
        value: '+687751234',
        prefix: '+687',
        phoneNumber: '751234',
      },
    ])(
      'should split value $value into $prefix and $phoneNumber',
      ({ value, prefix, phoneNumber }) => {
        renderPhoneNumberInput({ value })
        const countryCodeSelect = screen.getByRole('combobox')
        const phoneNumberInput = screen.getByRole('textbox')

        expect(countryCodeSelect).toHaveValue(prefix)
        expect(phoneNumberInput).toHaveValue(phoneNumber)
      }
    )
  })

  it('should give the correct value to the "onChange" functions', async () => {
    const onChangeFn = vi.fn()
    const onBlurFn = vi.fn()
    let changeEvent, blurEvent
    renderPhoneNumberInput({
      value: '+33612345678',
      onChange: onChangeFn,
      onBlur: onBlurFn,
    })

    // Changes phone number value
    const phoneNumberInput = screen.getByRole('textbox')
    await userEvent.clear(phoneNumberInput)
    await userEvent.type(phoneNumberInput, '8845678') // triggers "onChange"
    await userEvent.tab() // triggers "onBlur"

    // Expect change and blur events to have been called with the correct value
    changeEvent = onChangeFn.mock.lastCall?.[0]
    blurEvent = onBlurFn.mock.lastCall?.[0]
    ;[changeEvent, blurEvent].forEach((event) => {
      expect(event).toBeDefined()
      expect(event.target.name).toBe('phone')
      expect(event.target.value).toBe('+338845678')
    })

    // Then changes country code (prefix)
    const countryCodeSelect = screen.getByRole('combobox')
    await userEvent.selectOptions(countryCodeSelect, '+590') // triggers "onChange"
    await userEvent.tab() // triggers "onBlur"

    // Expect change and blur events to have been called with the correct value
    changeEvent = onChangeFn.mock.lastCall?.[0]
    blurEvent = onBlurFn.mock.lastCall?.[0]
    ;[changeEvent, blurEvent].forEach((event) => {
      expect(event).toBeDefined()
      expect(event.target.name).toBe('phone')
      expect(event.target.value).toBe('+5908845678')
    })
  })

  it('should expose a ref with the good value to the phone number input', () => {
    const refMock = vi.fn()
    renderPhoneNumberInput({ value: '+33687451542', ref: refMock })

    const inputRef = refMock.mock.lastCall?.[0] as HTMLInputElement

    expect(inputRef).toBeDefined()
    expect(inputRef.value).toBe('+33687451542')
  })
})
