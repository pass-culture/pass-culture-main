import React from 'react'
import { mount } from 'enzyme'
import { MemoryRouter } from 'react-router'
import IneligibleUnderEighteen from '../IneligibleUnderEighteen'

describe('under eighteen page', () => {
  it('should display an information text', () => {
    // Given
    const wrapper = mount(
      <MemoryRouter initialEntries={['/verification-eligibilite/trop-tot']}>
        <IneligibleUnderEighteen />
      </MemoryRouter>
    )
    // Then
    expect(wrapper.find({children:'Oh non !'})).toHaveLength(1)
    expect(wrapper.find({children:'Il est encore un peu tôt pour toi. Pour profiter du pass Culture, tu dois avoir 18 ans.'})).toHaveLength(1)
  })

  it('should render button to home page', () => {
    // Given
    const wrapper = mount(
      <MemoryRouter initialEntries={['/verification-eligibilite/trop-tot']}>
        <IneligibleUnderEighteen />
      </MemoryRouter>
    )
    // Then
    expect(wrapper.find('a[href="/beta"]').text()).toBe('Retourner à l’accueil')
  })
})
