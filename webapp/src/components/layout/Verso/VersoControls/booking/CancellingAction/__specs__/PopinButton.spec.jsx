import { mount } from 'enzyme'
import React from 'react'

import PopinButton from '../PopinButton'

describe('src | PopinButton', () => {
  it('should display a label', () => {
    // Given
    const props = {
      action: jest.fn(),
      label: 'Fake label',
    }

    // When
    const wrapper = mount(<PopinButton {...props} />)

    // Then
    const label = wrapper.find({ children: 'Fake label' })
    expect(label).toHaveLength(1)
  })

  describe('when cliking on button', () => {
    it('should disable it', () => {
      // Given
      const props = {
        action: jest.fn(),
        label: 'Fake label',
      }
      const wrapper = mount(<PopinButton {...props} />)

      // When
      wrapper.find('button').invoke('onClick')(props.action)

      // Then
      expect(wrapper.find('button').prop('disabled')).toBe(true)
      expect(props.action).toHaveBeenCalledTimes(1)
    })
  })
})
