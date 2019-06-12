import { shallow } from 'enzyme'
import React from 'react'
import LocationFields from '../LocationFields'
import { HiddenField } from '../../../../../layout/form/fields'

describe('src | components | pages | Venue | fields | LocationFields', () => {
  let props

  beforeEach(() => {
    props = {
      fieldReadOnlyBecauseFrozenFormSiret: true,
      form: {},
      formIsLocationFrozen: true,
      formLatitude: 1,
      formLongitude: 1,
      readOnly: true
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<LocationFields {...props}/>)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render an HiddenField component with the right props', () => {
      // when
      const wrapper = shallow(<LocationFields {...props}/>)

      // then
      const hiddenField = wrapper.find(HiddenField)
      expect(hiddenField).toHaveLength(1)
      expect(hiddenField.prop('name')).toBe('isLocationFrozen')
    })
  })
})
