// jest --env=jsdom ./src/components/share/tests/SharePopinContent --watch
import React from 'react'
import { shallow } from 'enzyme'

import SharePopinContent from '../SharePopinContent'
import CopyToClipboardButton from '../CopyToClipboardButton'

const dispatchMock = jest.fn()

describe('src | components | share | SharePopinContent', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: dispatchMock,
        options: {
          text: 'Fake Test',
          title: 'Fake Title',
          url: 'fake@url.com',
        },
        visible: true,
      }

      // when
      const wrapper = shallow(<SharePopinContent {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions', () => {
    describe('closeHandler', () => {
      describe('when options are true', () => {
        it('should call dispatch with good action parameters', () => {
          // given
          const props = {
            dispatch: dispatchMock,
            email: 'fake@email.com',
            options: {
              text: 'Fake Test',
              title: 'Fake Title',
              url: 'fake@url.com',
            },
            visible: true,
          }

          // when
          const wrapper = shallow(<SharePopinContent {...props} />).dive()
          wrapper.find('button').simulate('click')
          const expected = {
            options: false,
            type: 'TOGGLE_SHARE_POPIN',
          }

          // then
          expect(dispatchMock).toHaveBeenCalledWith(expected)
        })
      })
    })

    describe('onCopyHandler', () => {
      describe('when options are true', () => {
        it.skip('should update state', () => {
          // TODO Mock Transition status
          // given
          const props = {
            dispatch: dispatchMock,
            email: 'fake@email.com',
            options: {
              text: 'Fake Test',
              title: 'Fake Title',
              url: 'fake@url.com',
            },
            visible: true,
          }

          // when
          const wrapper = shallow(<SharePopinContent {...props} />)
          wrapper
            .dive()
            .find(CopyToClipboardButton)
            .simulate('click')
          const expected = {
            iscopied: true,
          }

          // then
          expect(wrapper.state()).toStrictEqual(expected)
        })
      })
    })
  })
})
