import { shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import OffererCreation from '../OffererCreation'
import OffererCreationForm from '../OffererCreationForm/OffererCreationForm'

describe('src | components | OffererCreation', () => {
  let props

  beforeEach(() => {
    props = {
      createNewOfferer: jest.fn(),
      showNotification: jest.fn(),
      closeNotification: jest.fn(),
      trackCreateOfferer: jest.fn(),
      redirectToOfferersList: jest.fn(),
    }
  })

  describe('event tracking', () => {
    it('should track offerer creation', () => {
      // given
      const state = {}
      const action = {
        payload: {
          datum: {
            id: 'Ty5645dgfd',
          },
        },
      }
      const wrapper = shallow(<OffererCreation {...props} />)

      // when
      wrapper.instance().onHandleSuccess(state, action)

      // then
      expect(props.trackCreateOfferer).toHaveBeenCalledWith('Ty5645dgfd')
    })
  })

  describe('render', () => {
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
      expect(title.title).toStrictEqual('Structure')
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

  describe('componentWillUnmount', () => {
    it('should close notification', () => {
      // when
      const wrapper = shallow(<OffererCreation {...props} />)
      wrapper.unmount()

      // expect
      expect(props.closeNotification).toHaveBeenCalledWith()
    })
  })
})
