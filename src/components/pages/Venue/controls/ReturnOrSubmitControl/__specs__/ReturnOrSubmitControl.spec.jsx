import { shallow } from 'enzyme'
import React from 'react'
import { NavLink } from 'react-router-dom'

import ReturnOrSubmitControl from '../ReturnOrSubmitControl'

describe('src | components | pages | Venue | controls | ReturnOrSubmitControl ', () => {
  let props

  beforeEach(() => {
    props = {
      canSubmit: true,
      isCreatedEntity: true,
      isRequestPending: true,
      offererId: 'ABC',
      readOnly: true,
    }
  })

  describe('render', () => {
    it('should display a NavLink with the right props when read only mode', () => {
      // given
      props.readOnly = true

      // when
      const wrapper = shallow(<ReturnOrSubmitControl {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink).toHaveLength(1)
      expect(navLink.prop('className')).toBe('button is-primary is-medium')
      expect(navLink.prop('to')).toBe('/structures/ABC')
    })

    it('should display a button with the right props when not read only mode, is not request pending, can submit, and is in creation mode', () => {
      // given
      props.readOnly = false

      // when
      const wrapper = shallow(<ReturnOrSubmitControl {...props} />)

      // then
      const button = wrapper.find('button')
      expect(button.prop('className')).toBe('button is-primary is-medium is-loading')
      expect(button.prop('disabled')).toBe(false)
      expect(button.prop('type')).toBe('submit')
      expect(button.text()).toBe('Créer')
    })

    it('should display a button with the right props when not read only mode, is request pending, can not submit, and is not in creation mode', () => {
      // given
      props.canSubmit = false
      props.readOnly = false
      props.isCreatedEntity = false
      props.isRequestPending = true

      // when
      const wrapper = shallow(<ReturnOrSubmitControl {...props} />)

      // then
      const button = wrapper.find('button')
      expect(button.prop('className')).toBe('button is-primary is-medium is-loading')
      expect(button.prop('disabled')).toBe(true)
      expect(button.prop('type')).toBe('submit')
      expect(button.text()).toBe('Valider')
    })
  })
})
