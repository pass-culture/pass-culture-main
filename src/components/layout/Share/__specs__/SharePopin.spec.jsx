import { mount } from 'enzyme'
import React from 'react'

import SharePopin from '../SharePopin'

describe('src | components | share | SharePopin', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      dispatch,
      options: {
        text: 'Fake Test',
        title: 'Fake Title',
        url: 'fake@url.com',
      },
      visible: true,
    }
  })

  describe('functions', () => {
    describe('closeHandler', () => {
      it('should call dispatch with good action parameters', () => {
        // given
        const wrapper = mount(<SharePopin {...props} />)
        const button = wrapper.find('button')

        // when
        button.simulate('click')

        // then
        expect(dispatch).toHaveBeenCalledWith({
          options: null,
          type: 'TOGGLE_SHARE_POPIN',
        })
      })
    })
  })
})
