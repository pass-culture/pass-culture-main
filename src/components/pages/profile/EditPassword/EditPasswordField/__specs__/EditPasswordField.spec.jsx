import { mount } from 'enzyme'
import React from 'react'

import EditPasswordField from '../EditPasswordField'

describe('edit password field', () => {
  let props

  beforeEach(() => {
    props = {
      label: 'fake label',
      placeholder: 'fake placeholder',
    }
  })

  it('should display a label with an input password and toggle button,', () => {
    // When
    const wrapper = mount(<EditPasswordField {...props} />)

    // Then
    const label = wrapper.find('label').text()
    expect(label).toBe('fake label')

    const input = wrapper.find('input')
    expect(input.prop('type')).toBe('password')
    expect(input.prop('placeholder')).toBe('fake placeholder')

    const button = wrapper.find('button')
    const toggleIcon = button.find('img[alt="Afficher le mot de passe"]')
    expect(toggleIcon).toHaveLength(1)
  })

  describe('when clicking on visibility toggle', () => {
    it('should reveal my password if hidden and change textual alternative and icon', () => {
      // Given
      const wrapper = mount(<EditPasswordField {...props} />)

      // When
      wrapper.find('button').invoke('onClick')()

      // Then
      const newPassword = wrapper.find('input').prop('type')
      expect(newPassword).toBe('text')
      const toggleIcon = wrapper.find('button img')
      expect(toggleIcon.prop('alt')).toBe('Masquer le mot de passe')
      expect(toggleIcon.prop('src')).toBe('http://localhost/icons/ico-eye-close.svg')
    })

    it('should hide my password if revealed and change textual alternative and icon', () => {
      // Given
      const wrapper = mount(<EditPasswordField {...props} />)

      // When
      wrapper.find('button').invoke('onClick')()
      wrapper.find('button').invoke('onClick')()

      // Then
      const newPassword = wrapper.find('input').prop('type')
      expect(newPassword).toBe('password')
      const toggleIcon = wrapper.find('button img')
      expect(toggleIcon.prop('alt')).toBe('Afficher le mot de passe')
      expect(toggleIcon.prop('src')).toBe('http://localhost/icons/ico-eye-open.svg')
    })
  })
})
