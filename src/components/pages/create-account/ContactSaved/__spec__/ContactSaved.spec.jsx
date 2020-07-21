import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import React from 'react'
import { act } from 'react-dom/test-utils'

import ContactSaved from '../ContactSaved'
import { Redirect } from 'react-router'

describe('contact saved page', () => {
  describe('on render', () => {
    it('should display an information text', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <ContactSaved />
        </MemoryRouter>
      )

      // then
      const contactSavedText = wrapper.find({ children: 'C’est noté !' })
      const informationText = wrapper.find({ children: 'Tu vas être redirigé dans 5 secondes...' })
      expect(contactSavedText).toHaveLength(1)
      expect(informationText).toHaveLength(1)
    })
  })

  describe('on redirection', () => {
    beforeEach(()=> {
      jest.useFakeTimers()
    })

    it('should redirect 5 secondes after render the contact saved page', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <ContactSaved />
        </MemoryRouter>
      )

      // then
      expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 5000)
    })

    it('should redirect to the home page', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <ContactSaved />
        </MemoryRouter>
      )
      act(() => {
        jest.runAllTimers()
      })
      wrapper.update()

      // then
      const contactSavedText = wrapper.find({ children: 'Tu vas être redirigé dans 5 secondes...' })
      expect(contactSavedText).toHaveLength(0)
      expect(wrapper.find(Redirect).prop('to')).toBe('/beta')
    })
  })
})
