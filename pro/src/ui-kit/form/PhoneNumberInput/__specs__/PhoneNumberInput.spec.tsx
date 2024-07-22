import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import React from 'react'

import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PLACEHOLDER_MAP } from '../constants'
import { PhoneNumberInput } from '../PhoneNumberInput'

vi.mock('libphonenumber-js', () => ({
  ...vi.importActual('libphonenumber-js'),
  parsePhoneNumberFromString: vi.fn(),
}))

const renderPhoneNumberInput = (label = 'Téléphone') => {
  render(
    <Formik initialValues={{}} onSubmit={() => {}}>
      <PhoneNumberInput name="phone" label={label} />
    </Formik>
  )
}

describe('PhoneNumberInput', () => {
  it('should show default placeholder', () => {
    renderPhoneNumberInput()

    const defaultCountryCodeOption = PHONE_CODE_COUNTRY_CODE_OPTIONS[0]!
    const defaultPlaceholder = PLACEHOLDER_MAP[defaultCountryCodeOption.value]

    expect(screen.getByText(defaultCountryCodeOption.label)).toBeInTheDocument()
    expect(defaultPlaceholder).toBeDefined()
    expect(
      screen.getByPlaceholderText(defaultPlaceholder as string)
    ).toBeInTheDocument()
  })

  it('should change placeholder when user change country code', async () => {
    renderPhoneNumberInput()
    const countryCodeSelect = screen.getByLabelText('Indicatif téléphonique')

    await userEvent.selectOptions(countryCodeSelect, '+590')

    const guadeloupePlaceholder = PLACEHOLDER_MAP['GP']
    expect(guadeloupePlaceholder).toBeDefined()
    expect(
      screen.getByPlaceholderText(guadeloupePlaceholder as string)
    ).toBeInTheDocument()
  })

  it('should not show an error if input has not been touched', () => {
    renderPhoneNumberInput()
    expect(
      screen.queryByText(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
    ).not.toBeInTheDocument()
  })

  it('should show an error if user touched input and did not enter any phone number', async () => {
    renderPhoneNumberInput()
    const input = screen.getByText('Numéro de téléphone')

    await userEvent.click(input)
    await userEvent.tab()

    expect(
      screen.queryByText(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
    ).toBeInTheDocument()
  })

  it('should call phone validation with country code', async () => {
    renderPhoneNumberInput()
    const countryCodeSelect = screen.getByLabelText('Indicatif téléphonique')
    await userEvent.selectOptions(countryCodeSelect, '+590')

    const input = screen.getByLabelText('Numéro de téléphone')

    await userEvent.type(input, '123')
    await userEvent.tab()

    expect(parsePhoneNumberFromString).toHaveBeenLastCalledWith('123', 'GP')
    expect(
      screen.queryByText(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
    ).toBeInTheDocument()

    await userEvent.selectOptions(countryCodeSelect, '+33')

    expect(parsePhoneNumberFromString).toHaveBeenLastCalledWith('123', 'FR')
  })
})
