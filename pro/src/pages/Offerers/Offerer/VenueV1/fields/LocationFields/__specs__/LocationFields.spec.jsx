import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'
import { Form } from 'react-final-form'

import LocationFields from '../LocationFields'

describe('src | components | pages | Venue | fields | LocationFields', () => {
  let props

  beforeEach(() => {
    props = {
      fieldReadOnlyBecauseFrozenFormSiret: true,
      form: {},
      formIsLocationFrozen: true,
      formLatitude: 1,
      formLongitude: 1,
      readOnly: true,
      isAddressRequired: false,
    }
  })

  const renderLocationFields = props => {
    return render(
      <Form
        onSubmit={() => {}}
        render={() => <LocationFields {...props} />}
      ></Form>
    )
  }

  describe('render', () => {
    it('should display an HiddenField component with the right props', () => {
      // when
      const { container } = renderLocationFields(props)
      expect(container.querySelector('input[type=hidden]')).toBeInTheDocument()
    })

    it('should display an AddressField component with the right props', () => {
      // when
      renderLocationFields(props)

      // then
      const addressField = screen.getAllByRole('textbox')[0]
      expect(addressField).toHaveAttribute('readOnly')
      expect(addressField).toHaveAttribute('name', 'address')
      expect(addressField).not.toHaveAttribute('required')
    })

    it('should display an AddressField component with required address field', () => {
      // when
      props.isAddressRequired = true
      props.readOnly = false
      props.fieldReadOnlyBecauseFrozenFormSiret = false
      renderLocationFields(props)

      // then
      const addressField = screen.getByRole('combobox')
      expect(addressField).toHaveAttribute('name', 'address')
      expect(addressField).toHaveAttribute('required')
    })

    it('should display two TextField components with the right props', () => {
      // when
      renderLocationFields(props)

      // then
      const postalCodeField = screen.getByLabelText('Code postal :')
      expect(postalCodeField).toHaveAttribute('autoComplete', 'postal-code')
      expect(postalCodeField).toHaveAttribute('name', 'postalCode')
      expect(postalCodeField).toHaveAttribute('readonly')
      expect(postalCodeField).toHaveAttribute('required')
      const cityField = screen.getByLabelText('Ville :')
      expect(cityField).toHaveAttribute('autoComplete', 'address-level2')
      expect(cityField).toHaveAttribute('name', 'city')
      expect(cityField).toHaveAttribute('readonly')
      expect(cityField).toHaveAttribute('required')
    })

    it('should display two NumberField with the right props', () => {
      // when
      renderLocationFields(props)

      // then

      const postalCodeField = screen.getByLabelText('Latitude :')
      expect(postalCodeField).toHaveAttribute('name', 'latitude')
      expect(postalCodeField).toHaveAttribute('readonly')
      expect(postalCodeField).toHaveAttribute('required')
      const cityField = screen.getByLabelText('Longitude :')
      expect(cityField).toHaveAttribute('name', 'longitude')
      expect(cityField).toHaveAttribute('readonly')
      expect(cityField).toHaveAttribute('required')
    })
  })
})
