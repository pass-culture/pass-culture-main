import React from 'react'
import { shallow } from 'enzyme'

import ShareButtonContent, {
  getCopyToClipboardButton,
  getMailToLinkButton,
  getCloseButton,
} from '../ShareButtonContent'

const dispatchMock = jest.fn()

describe('src | components | share | getCopyToClipboardButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const onClick = () => {}
      const url = 'http://foo.com'
      // when
      const wrapper = shallow(getCopyToClipboardButton(url, onClick))
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})

describe('src | components | share | getMailToLinkButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const email = 'foo@bar.com'
      const headers = {
        subject: 'Fake title',
        url: 'http://www.fake-url.com',
      }

      // when
      const wrapper = shallow(getMailToLinkButton(email, headers))
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})

describe('src | components | share | getCloseButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const onClose = () => {}
      // when
      const wrapper = shallow(getCloseButton(onClose))
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
        offerName: 'Fake offer name',
        text: 'Fake text',
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
            offerName: 'Fake offer name',
            text: 'Fake text',
            url: 'http://www.fake-url.com',
          }

          // when
          const wrapper = shallow(<ShareButtonContent {...props} />)
          wrapper.find('button').simulate('click')
          const expected = {
            options: {
              buttons: expect.any(Array),
              text: 'Comment souhaitez-vous partager cette offre ?',
              title: 'Fake offer name',
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
