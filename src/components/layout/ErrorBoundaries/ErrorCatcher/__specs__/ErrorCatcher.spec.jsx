import { mount } from 'enzyme'
import React from 'react'

import { Children } from '../../ErrorsPage/__specs__/Children'
import ErrorCatcher from '../ErrorCatcher'

describe('src | layout | ErrorCatcher', () => {
  describe('when exception did not throw', () => {
    it('should display the children', () => {
      // when
      const wrapper = mount(
        <ErrorCatcher>
          <Children />
        </ErrorCatcher>
      )

      // then
      const children = wrapper.find({ children: 'any child component' })
      expect(children).toHaveLength(1)
    })
  })

  describe('when an exception throwed', () => {
    it('should display a specific error message', () => {
      // given
      const error = new Error('This is an error!')

      // when
      const wrapper = mount(
        <ErrorCatcher>
          <Children />
        </ErrorCatcher>
      )
      wrapper.find(Children).simulateError(error)

      // then
      const title = wrapper.find({ children: 'Une erreur est survenue.' })
      const link = wrapper.find('a').find({ children: 'Retour aux offres' })
      expect(title).toHaveLength(1)
      expect(link).toHaveLength(1)
    })
  })
})
