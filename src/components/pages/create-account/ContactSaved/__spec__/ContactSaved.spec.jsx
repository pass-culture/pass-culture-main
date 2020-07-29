import { mount } from 'enzyme'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'

import ContactSaved from '../ContactSaved'

describe('contact saved page', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

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

  it('should start a counter with 1 second inverval', () => {
    // when
    mount(
      <MemoryRouter>
        <ContactSaved />
      </MemoryRouter>
    )

    // then
    expect(setInterval).toHaveBeenCalledWith(expect.any(Function), 1000)
  })

  it('should redirect after 5 seconds and clear the counter', () => {
    // given
    const wrapper = mount(
      <MemoryRouter>
        <ContactSaved />
      </MemoryRouter>
    )

    // when
    act(() => jest.advanceTimersByTime(5000))
    wrapper.update()

    // then
    const redirectionLink = wrapper.find('Redirect').prop(`to`)
    expect(redirectionLink).toBe('/beta')

    // when
    wrapper.unmount()

    // then
    expect(clearInterval).toHaveBeenCalledTimes(1)
  })
})
