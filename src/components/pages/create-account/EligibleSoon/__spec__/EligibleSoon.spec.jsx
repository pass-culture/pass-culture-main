import { mount, shallow } from 'enzyme'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'
import EligibleSoon from '../../EligibleSoon/EligibleSoon'
import { handleCheckEmailFormat } from '../../utils/checkEmailFormat'

jest.mock('../../utils/checkEmailFormat', () => {
  return {
    handleCheckEmailFormat: jest.fn(),
  }
})

jest.mock('../../../../../utils/config', () => ({
  API_URL: 'my-localhost',
}))

describe('eligible soon page', () => {
  let props
  beforeEach(() => {
    props = {
      birthDate: '02/02/2003',
      body: 'Tu es bientôt éligible.',
      postalCode: '93800',
      title: 'Bientôt !',
      visual: React.createElement('img'),
    }
  })

  it('should inform the user that he is soon to be eligible', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <EligibleSoon {...props} />
      </MemoryRouter>
    )

    // Then
    const mainInformation = wrapper.find({ children: 'Bientôt !' }).closest('h1')
    expect(mainInformation).toHaveLength(1)
  })

  it('should allow the user to enter an email address', () => {
    // When
    const wrapper = shallow(<EligibleSoon {...props} />)

    // Then
    const emailInput = wrapper.find('form').find('input[type="email"]')
    expect(emailInput).toHaveLength(1)
  })

  it('should not allow the user to save his email address when it is invalid', () => {
    // Given
    handleCheckEmailFormat.mockReturnValue(false)

    // When
    const wrapper = shallow(<EligibleSoon {...props} />)

    // Then
    const submitButton = wrapper
      .find('form')
      .find({ children: 'Rester en contact' })
      .closest('button[type="submit"]')
    expect(submitButton).toHaveLength(1)
    expect(submitButton.prop('disabled')).toBe(true)
  })

  it('should allow the user to save his email address when it is valid', () => {
    // Given
    handleCheckEmailFormat.mockReturnValue(true)

    // When
    const wrapper = shallow(<EligibleSoon {...props} />)

    // Then
    const submitButton = wrapper
      .find('form')
      .find({ children: 'Rester en contact' })
      .closest('button[type="submit"]')
    expect(submitButton).toHaveLength(1)
    expect(submitButton.prop('disabled')).toBe(false)
  })

  it('should allow the user to go back to home page', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <EligibleSoon {...props} />
      </MemoryRouter>
    )

    // Then
    const goBackHomeLink = wrapper
      .find({ children: 'Retourner à l’accueil' })
      .last()
      .closest('a[href="/beta"]')
    expect(goBackHomeLink).toHaveLength(1)
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
