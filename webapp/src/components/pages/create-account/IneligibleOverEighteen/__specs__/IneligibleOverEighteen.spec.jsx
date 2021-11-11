import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import IneligibleOverEighteen from '../IneligibleOverEighteen'

jest.mock('../../../../../utils/config', () => ({ SUPPORT_EMAIL: 'support@example.com' }))

describe('ineligible over eighteen page', () => {
  it('should have a link to send an email to the support team', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <IneligibleOverEighteen />
      </MemoryRouter>
    )

    // Then
    expect(wrapper.find('a[href="mailto:support@example.com"]')).toHaveLength(1)
  })

  it('should have a link to go back to home', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <IneligibleOverEighteen />
      </MemoryRouter>
    )

    // Then
    expect(wrapper.find('a[href="/beta"]')).toHaveLength(1)
  })
})
