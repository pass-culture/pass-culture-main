import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { Animation } from '../../../pages/create-account/Animation/Animation'
import Loader from '../Loader'

describe('layout | Loader', () => {
  describe('when no error', () => {
    it('should display the loading message', () => {
      // When
      const wrapper = mount(
        <MemoryRouter>
          <Loader />
        </MemoryRouter>
      )

      // Then
      const animation = wrapper.find(Animation)
      const sentence = wrapper.find({ children: 'Chargement en cours…' })
      expect(animation).toHaveLength(1)
      expect(sentence).toHaveLength(1)
    })
  })
})
