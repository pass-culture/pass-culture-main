import { shallow } from 'enzyme'
import React from 'react'

import HiddenField from 'components/layout/form/fields/HiddenField'
import NumberField from 'components/layout/form/fields/NumberField'
import TextField from 'components/layout/form/fields/TextField'

import AddressField from '../AddressField'
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

  describe('render', () => {
    it('should display an HiddenField component with the right props', () => {
      // when
      const wrapper = shallow(<LocationFields {...props} />)

      // then
      const hiddenField = wrapper.find(HiddenField)
      expect(hiddenField).toHaveLength(1)
      expect(hiddenField.prop('name')).toBe('isLocationFrozen')
    })

    it('should display an AddressField component with the right props', () => {
      // when
      const wrapper = shallow(<LocationFields {...props} />)

      // then
      const addressField = wrapper.find(AddressField)
      expect(addressField).toHaveLength(1)
      expect(addressField.prop('form')).toStrictEqual({})
      expect(addressField.prop('label')).toBe('Numéro et voie : ')
      expect(addressField.prop('latitude')).toBe(1)
      expect(addressField.prop('longitude')).toBe(1)
      expect(addressField.prop('name')).toBe('address')
      expect(addressField.prop('readOnly')).toBe(true)
      expect(addressField.prop('required')).toBe(false)
      expect(addressField.prop('withMap')).toBe(true)
    })

    it('should display an AddressField component with required address field', () => {
      // when
      props.isAddressRequired = true
      const wrapper = shallow(<LocationFields {...props} />)

      // then
      const addressField = wrapper.find(AddressField)
      expect(addressField).toHaveLength(1)
      expect(addressField.prop('required')).toBe(true)
    })

    it('should display two TextField components with the right props', () => {
      // when
      const wrapper = shallow(<LocationFields {...props} />)

      // then
      const textFields = wrapper.find(TextField)
      expect(textFields).toHaveLength(2)
      expect(textFields.at(0).prop('autoComplete')).toBe('postal-code')
      expect(textFields.at(0).prop('innerClassName')).toBe('col-33')
      expect(textFields.at(0).prop('label')).toBe('Code postal : ')
      expect(textFields.at(0).prop('name')).toBe('postalCode')
      expect(textFields.at(0).prop('readOnly')).toBe(true)
      expect(textFields.at(0).prop('required')).toBe(true)
      expect(textFields.at(1).prop('autoComplete')).toBe('address-level2')
      expect(textFields.at(1).prop('innerClassName')).toBe('col-66')
      expect(textFields.at(1).prop('label')).toBe('Ville : ')
      expect(textFields.at(1).prop('name')).toBe('city')
      expect(textFields.at(1).prop('readOnly')).toBe(true)
      expect(textFields.at(1).prop('required')).toBe(true)
    })

    it('should display two NumberField with the right props', () => {
      // when
      const wrapper = shallow(<LocationFields {...props} />)

      // then
      const numberFields = wrapper.find(NumberField)
      expect(numberFields).toHaveLength(2)
      expect(numberFields.at(0).prop('innerClassName')).toBe('col-33')
      expect(numberFields.at(0).prop('label')).toBe('Latitude : ')
      expect(numberFields.at(0).prop('name')).toBe('latitude')
      expect(numberFields.at(0).prop('readOnly')).toBe(true)
      expect(numberFields.at(0).prop('required')).toBe(true)
      expect(numberFields.at(0).prop('step')).toBe(0.000001)
      expect(numberFields.at(1).prop('innerClassName')).toBe('col-33')
      expect(numberFields.at(1).prop('label')).toBe('Longitude : ')
      expect(numberFields.at(1).prop('name')).toBe('longitude')
      expect(numberFields.at(1).prop('readOnly')).toBe(true)
      expect(numberFields.at(1).prop('required')).toBe(true)
      expect(numberFields.at(1).prop('step')).toBe(0.000001)
    })
  })
})
