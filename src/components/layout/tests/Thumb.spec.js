import React from 'react'
import { shallow } from 'enzyme'

import Thumb from '../Thumb'

describe('src | components | pages | Thumb', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        title: 'fake title',
      }

      // when
      const wrapper = shallow(<Thumb {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('without Mediation', () => {
      // given
      const props = {
        src: 'http://fake.url',
      }
      it('should display backgound div', () => {
        // when
        const wrapper = shallow(<Thumb {...props} />)
        const backgroundDiv = wrapper.find('.background').props()
        const thumbDiv = wrapper
          .find('.thumb')
          .childAt(1)
          .props()

        // then
        expect(backgroundDiv.style.backgroundImage).toStrictEqual(
          "url('http://fake.url')"
        )
        expect(backgroundDiv.style.backgroundSize).toStrictEqual(null)
        expect(thumbDiv.style.backgroundImage).toStrictEqual("url('http://fake.url')")
        expect(thumbDiv.style.backgroundSize).toStrictEqual(null)
        expect(thumbDiv.className).toStrictEqual('image translatable')
      })
    })
    describe('with Mediation', () => {
      it('should display backgound div', () => {
        // given
        const props = {
          src: 'http://fake.url',
          translated: true,
          withMediation: {
            fakeMediation: 'fakeMediation',
          },
        }

        // when
        const wrapper = shallow(<Thumb {...props} />)
        const backgroundDiv = wrapper.find('.background')
        const thumbDiv = wrapper
          .find('.thumb')
          .childAt(0)
          .props()

        // then
        expect(backgroundDiv.exists()).toStrictEqual(false)
        expect(thumbDiv.style.backgroundImage).toStrictEqual("url('http://fake.url')")
        expect(thumbDiv.style.backgroundSize).toStrictEqual('cover')
        expect(thumbDiv.className).toStrictEqual('image translatable translated')
      })
    })
  })
})
