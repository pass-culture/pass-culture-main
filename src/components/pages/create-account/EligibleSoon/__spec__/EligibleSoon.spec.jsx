import { mount } from 'enzyme'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'

import { handleCheckEmailFormat } from '../../utils/checkEmailFormat'
import EligibleSoon from '../EligibleSoon'

jest.mock('../../utils/checkEmailFormat', () => {
  return {
    handleCheckEmailFormat: jest.fn(),
  }
})
jest.mock('../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

describe('eligible soon page', () => {
  const props = {
    birthDate: '02/02/2003',
    postalCode: '93800',
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
      expect(wrapper.find({ children: 'Plus que quelques mois d’attente !' })).toHaveLength(1)
      expect(
        wrapper.find({
          children:
            'Pour profiter du pass Culture, tu dois avoir 18 ans. Entre ton adresse email : nous t’avertirons dès que tu seras éligible.',
        })
      ).toHaveLength(1)
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
      const submitButton = wrapper.find({ children: 'Rester en contact' })
      const emailInput = wrapper.find('input[type="email"]')

      // when
      act(() => {
        emailInput.invoke('onChange')({ target: { value: 'invalid@email' } })
      })

      // then
      expect(submitButton.prop('disabled')).toBe(false)
    })
  })

  describe('when submitting form', () => {
    beforeEach(() => {
      jest.spyOn(global, 'fetch').mockImplementation(() => new Promise())
    })

    it('should fetch API with proper params', async () => {
      // Given
      global.fetch.mockResolvedValueOnce({ status: 201 })

      const userInformations = {
        email: 'valid@example.com',
        dateOfBirth: '2003-02-02',
        departmentCode: '93',
      }

      const wrapper = mount(
        <MemoryRouter>
          <EligibleSoon {...props} />
        </MemoryRouter>
      )

      const emailInput = wrapper.find('input[type="email"]')

      // when
      act(() => {
        emailInput.invoke('onChange')({ target: { value: 'valid@example.com' } })
      })
      wrapper.update()

      const form = wrapper.find('form')
      await act(async () => {
        await form.invoke('onSubmit')({
          preventDefault: jest.fn(),
        })
      })
      wrapper.update()

      // Then
      expect(global.fetch).toHaveBeenCalledTimes(1)
      expect(global.fetch).toHaveBeenCalledWith('my-localhost/mailing-contacts', {
        body: JSON.stringify(userInformations),
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        method: 'POST',
      })
    })

    describe('when API returns 201 code', () => {
      it('should display contact saved page', async () => {
        // Given
        global.fetch.mockResolvedValueOnce({ status: 201 })

        const wrapper = mount(
          <MemoryRouter>
            <EligibleSoon {...props} />
          </MemoryRouter>
        )

        const form = wrapper.find('form')
        const emailInput = wrapper.find('input[type="email"]')

        // when
        act(() => {
          emailInput.invoke('onChange')({ target: { value: 'valid@example.com' } })
        })
        wrapper.update()

        await act(async () => {
          await form.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'C’est noté !' })).toHaveLength(1)
      })
    })

    describe('when API does not return 201 code', () => {
      it('should throw an error', async () => {
        global.fetch.mockResolvedValueOnce({ status: 400 })

        // Given
        const wrapper = mount(
          <MemoryRouter>
            <EligibleSoon {...props} />
          </MemoryRouter>
        )

        const form = wrapper.find('form')
        const emailInput = wrapper.find('input[type="email"]')

        // when
        act(() => {
          emailInput.invoke('onChange')({ target: { value: 'valid@example.com' } })
        })
        wrapper.update()

        const failOnSubmit = async () =>
          await act(
            async () =>
              await form.invoke('onSubmit')({
                preventDefault: jest.fn(),
              })
          )

        // then
        await expect(failOnSubmit()).rejects.toThrow(
          "Erreur lors de l'enregistrement de l'adresse e-mail"
        )
      })
    })
  })
})
