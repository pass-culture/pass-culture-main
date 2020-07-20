import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import { act } from 'react-dom/test-utils'

import EligibleSoon from '../EligibleSoon'
import { handleCheckEmailFormat } from '../../utils/checkEmailFormat'

jest.mock('../../utils/checkEmailFormat', () => {
  return {
    handleCheckEmailFormat: jest.fn(),
  }
})

describe('eligible soon page', () => {
  const props =  {
    birthDate:'02/02/2003',
    postalCode:'93800'
  }
  describe('render', () => {
    it('should display informations text', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibleSoon {...props} />
        </MemoryRouter>
      )

      // then
      expect(wrapper.find({children: 'Plus que quelques mois d’attente !'})).toHaveLength(1)
      expect(wrapper.find({children: 'Pour profiter du pass Culture, tu dois avoir 18 ans. Entre ton adresse email : nous t’avertirons dès que tu seras éligible.'})).toHaveLength(1)
    })

    it('should display a go back home link', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibleSoon {...props} />
        </MemoryRouter>
      )

      // then
      const goBackHomeLink = wrapper.find('a[href="/beta"]')
      expect(goBackHomeLink).toHaveLength(1)
    })

    it('should display an email form', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibleSoon {...props} />
        </MemoryRouter>
      )

      // then
      const emailInput = wrapper.find('input[type="email"]')
      const submitButton = wrapper.find('button[type="submit"]')
      expect(emailInput).toHaveLength(1)
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('disabled')).toBe(true)
    })
  })

  describe('when email value is valid', () => {
    it('should enable the submit button', () => {
      // when
      handleCheckEmailFormat.mockReturnValue(true)

      const wrapper = mount(
        <MemoryRouter>
          <EligibleSoon {...props} />
        </MemoryRouter>
      )
      const submitButton = wrapper.find({children: 'Rester en contact'})
      const emailInput = wrapper.find('input[type="email"]')

      // when
      act(() => {
        emailInput.invoke('onChange')({target: {value: 'invalid@email'}})
      })

      // then
      expect(submitButton.prop('disabled')).toBe(false)
    })
  })
})
