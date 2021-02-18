import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import EditEmail from '../EditEmail'
import { act } from 'react-dom/test-utils'

describe('change email page', () => {
  describe('when filling the email field', () => {
    it('should add an error message when the email is invalid', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EditEmail />
        </MemoryRouter>
      )
      const newEmailInput = wrapper.find('input[name="new-email"]')

      // when
      act(() => {
        newEmailInput.invoke('onChange')({ target: { value: 'wrongemail.com' } })
      })
      wrapper.update()

      // then

    })
  })
})
