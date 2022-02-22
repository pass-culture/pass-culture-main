import { shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import OffererCreation from '../OffererCreation'
import OffererCreationForm from '../OffererCreationForm/OffererCreationForm'
import OffererCreationUnavailable from '../OffererCreationUnavailable/OffererCreationUnavailable'

describe('src | components | OffererCreation', () => {
  let props

  beforeEach(() => {
    props = {
      isEntrepriseApiDisabled: false,
      showNotification: jest.fn(),
      redirectAfterSubmit: jest.fn(),
    }
  })

  describe('render', () => {
    it('should render a OffererCreationUnavailable component when pro offerer creation is disabled', () => {
      props.isEntrepriseApiDisabled = true
      const wrapper = shallow(<OffererCreation {...props} />)

      expect(wrapper.find(OffererCreationUnavailable)).toHaveLength(1)
    })

    it('should render a OffererCreation component with default props', () => {
      // when
      const wrapper = shallow(<OffererCreation {...props} />)

      // then
      expect(wrapper.prop('createNewOfferer')).toBe()
      expect(wrapper.prop('showNotification')).toBe()
    })

    it('should display "Structure" title', () => {
      // given
      const wrapper = shallow(<OffererCreation {...props} />)

      // when
      const title = wrapper.find('Titles').props()

      // then
      expect(title.title).toBe('Structure')
    })

    it('should display offerer creation form', () => {
      // when
      const wrapper = shallow(<OffererCreation {...props} />)

      // then
      const form = wrapper.find(Form)
      const componentProp = form.prop('component')
      expect(componentProp).toBe(OffererCreationForm)
    })
  })
})
