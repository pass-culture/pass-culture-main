import { shallow } from 'enzyme'
import React from 'react'

import ShareButton from '../ShareButton'

describe('src | components | layout | Share | ShareButton | ShareButton', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      closePopin: () => {},
      trackShareOffer: () => {},
      offerName: 'Fake offer name',
      openPopin: () => {},
      text: 'Fake text',
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
    describe('when there is not native sharing', () => {
      it('should call openPopin with good options', () => {
        // given
        const openPopinMock = jest.fn()
        const props = {
          closePopin: () => {},
          email: 'foo@bar.com',
          offerName: 'Fake offer name',
          openPopin: openPopinMock,
          text: 'Fake text',
          trackShareOffer: () => {},
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
