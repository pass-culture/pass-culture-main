import React from 'react'
import { shallow } from 'enzyme'

import ShareButtonContent from '../ShareButtonContent'

const dispatchMock = jest.fn()

describe('src | components | share | ShareButtonContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: dispatchMock,
        title: 'Fake title',
        url: 'http://www.fake-url.com',
      }

      // when
      const wrapper = shallow(<ShareButtonContent {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions', () => {
    describe('onClickShare', () => {
      describe('when there is not native sharing', () => {
        it('should call dispatch with good action parameters', () => {
          // given
          const props = {
            dispatch: dispatchMock,
            title: 'Fake title',
            url: 'http://www.fake-url.com',
          }

          // when
          const wrapper = shallow(<ShareButtonContent {...props} />)
          wrapper.find('button').simulate('click')
          const expected = {
            options: {
              text: 'Comment souhaitez-vous partager cette offre ?',
              title: 'Fake title',
              url: 'http://www.fake-url.com',
            },
            type: 'TOGGLE_SHARE_POPIN',
          }

          // then
          expect(dispatchMock).toHaveBeenCalledWith(expected)
        })
      })
    })
  })
})
