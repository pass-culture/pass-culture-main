import { shallow } from 'enzyme'
import React from 'react'

import Thumb from '../Thumb'

describe('src | components | pages | Thumb', () => {
  describe('render', () => {
    describe('with Mediation', () => {
      it('should display backgound div', () => {
        // given
        const props = {
          src: 'http://fake.url',
          translated: true,
        }

        // when
        const wrapper = shallow(<Thumb {...props} />)
        const thumbDiv = wrapper
          .find('.thumb')
          .childAt(0)
          .props()

        // then
        expect(thumbDiv.style.backgroundImage).toStrictEqual("url('http://fake.url')")
        expect(thumbDiv.style.backgroundSize).toStrictEqual('cover')
        expect(thumbDiv.className).toStrictEqual('image translatable translated')
      })
    })
  })
})
