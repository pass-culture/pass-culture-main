import { mount } from 'enzyme'
import React from 'react'

import Titles from '../Titles'

describe('src | components | layout | Titles', () => {
  describe('render', () => {
    describe('subtitle', () => {
      it('should display subtitle when given', () => {
        // given
        const props = {
          subtitle: 'Fake subtitle',
          title: 'Fake title',
        }

        // when
        const wrapper = mount(<Titles {...props} />)
        const subtitle = wrapper.find('h2')

        // then
        expect(subtitle).toHaveLength(1)
        expect(subtitle.text()).toBe('FAKE SUBTITLE')
      })
    })
  })
})
