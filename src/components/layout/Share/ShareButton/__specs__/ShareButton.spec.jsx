import { shallow } from 'enzyme'
import React from 'react'

import ShareButton from '../ShareButton'
import NavigatorShareAPI from '../NavigatorShareAPI'

describe('components | ShareButton', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      closePopin: () => {},
      offerName: 'Fake offer name',
      openPopin: () => {},
      text: 'Fake text',
      trackShareOfferByLink: () => {},
      trackShareOfferByMail: () => {},
      url: 'http://www.fake-url.com',
    }

    // when
    const wrapper = shallow(<ShareButton {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('onCloseHandler', () => {
    describe('when close the modal', () => {
      it('should call closePopin with good action parameters', () => {
        // given
        const openPopinMock = jest.fn()
        const props = {
          closePopin: jest.fn(),
          email: 'foo@bar.com',
          offerName: 'Fake offer name',
          openPopin: openPopinMock,
          text: 'Fake text',
          trackShareOfferByLink: () => {},
          trackShareOfferByMail: () => {},
          url: 'http://www.fake-url.com',
        }

        // when
        const wrapper = shallow(<ShareButton {...props} />)
        wrapper.instance().onCloseHandler()

        // then
        expect(props.closePopin).toHaveBeenCalledWith()
        expect(wrapper.state('isCopied')).toBe(false)
      })
    })
  })

  describe('handleOnClickShare', () => {
    describe('when the share API is available', () => {
      let navigatorShareAPI
      beforeEach(() => {
        navigatorShareAPI = jest.spyOn(NavigatorShareAPI, 'share')
      })

      afterEach(() => {
        navigatorShareAPI.mockClear()
      })

      describe('when sharing is cancelled', () => {
        class AbortError extends Error {
          constructor() {
            super()
            this.name = 'AbortError'
          }
        }

        it('should catch the exception if its name is AbortError', async () => {
          // given
          const openPopinMock = jest.fn()
          const props = {
            closePopin: () => {},
            email: 'foo@bar.com',
            offerName: 'Fake offer name',
            openPopin: openPopinMock,
            text: 'Fake text',
            trackShareOfferByLink: () => {},
            trackShareOfferByMail: () => {},
            url: 'http://www.fake-url.com',
          }
          const wrapper = shallow(<ShareButton {...props} />)

          // when
          navigatorShareAPI.mockRejectedValue(new AbortError('Should not be thrown'))

          // then
          expect(await wrapper.instance().handleOnClickShare()).not.toBeDefined()
        })
      })

      describe('when sharing is failing', () => {
        it('should throw the exception if its name is different from AbortError', async () => {
          const error = new Error()
          navigatorShareAPI.mockRejectedValue(error)

          // given
          const openPopinMock = jest.fn()
          const props = {
            closePopin: () => {},
            email: 'foo@bar.com',
            offerName: 'Fake offer name',
            openPopin: openPopinMock,
            text: 'Fake text',
            trackShareOfferByLink: () => {},
            trackShareOfferByMail: () => {},
            url: 'http://www.fake-url.com',
          }

          // when
          const wrapper = shallow(<ShareButton {...props} />)
          const sharingPromise = wrapper.instance().handleOnClickShare()

          await expect(sharingPromise).rejects.toBe(error)
        })
      })
    })

    describe('when there is not native sharing', () => {
      it('should call openPopin with good options', () => {
        // given
        jest.spyOn(NavigatorShareAPI, 'share').mockImplementation(() => undefined)
        const openPopinMock = jest.fn()
        const props = {
          closePopin: () => {},
          email: 'foo@bar.com',
          offerName: 'Fake offer name',
          openPopin: openPopinMock,
          text: 'Fake text',
          trackShareOfferByLink: () => {},
          trackShareOfferByMail: () => {},
          url: 'http://www.fake-url.com',
        }

        // when
        const wrapper = shallow(<ShareButton {...props} />)
        wrapper.find('button').simulate('click')

        // then
        expect(openPopinMock).toHaveBeenCalledWith({
          buttons: expect.any(Array),
          text: 'Comment souhaitez-vous partager cette offre ?',
          title: 'Fake offer name',
        })
      })
    })
  })
})
