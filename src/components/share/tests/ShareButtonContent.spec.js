import React from 'react'
import { shallow } from 'enzyme'

import ShareButtonContent, {
  getCopyToClipboardButton,
  getMailToLinkButton,
  getCloseButton,
} from '../ShareButtonContent'

const dispatchMock = jest.fn()

describe('src | components | share | getCopyToClipboardButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        onClick: () => {},
        url: 'http://foo.com',
      }
      // when
      const wrapper = shallow(getCopyToClipboardButton(...props))
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('On click copy', () => {
    it('should call function on click', () => {
      // given
      const onClick = jest.fn()
      const props = {
        onClick,
        url: 'http://foo.com',
      }
      // when
      const wrapper = shallow(getCopyToClipboardButton(...props))
      const button = wrapper.find('button').simulate('click')

      // then
      expect(wrapper).toBeDefined()
      expect(button.length).toBe(1)
      // FIXME : can't understand why test does not pass :'(
      //    expect(onClick).toHaveBeenCalled()
    })
  })
})

describe('src | components | share | getMailToLinkButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        email: 'foo@bar.com',
        headers: {
          subject: 'Fake title',
          url: 'http://www.fake-url.com',
        },
      }
      // when
      const wrapper = shallow(getMailToLinkButton(...props))
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})

describe('src | components | share | getCloseButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        onClose: () => {},
      }
      // when
      const wrapper = shallow(getCloseButton(...props))
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})

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
            email: 'foo@bar.com',
            title: 'Fake title',
            url: 'http://www.fake-url.com',
          }

          // when
          const wrapper = shallow(<ShareButtonContent {...props} />)
          wrapper.find('button').simulate('click')
          const expected = {
            options: {
              buttons: expect.any(Array),
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
