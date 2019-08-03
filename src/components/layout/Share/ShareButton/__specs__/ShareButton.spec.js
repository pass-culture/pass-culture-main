import React from 'react'
import { shallow } from 'enzyme'

import ShareButton from '../ShareButton'

const dispatchMock = jest.fn()

describe('src | components | share | ShareButton', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      dispatch: dispatchMock,
      offerName: 'Fake offer name',
      text: 'Fake text',
      url: 'http://www.fake-url.com',
    }

    // when
    const wrapper = shallow(<ShareButton {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleOnClickShare', () => {
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
        const wrapper = shallow(<ShareButton {...props} />)
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
