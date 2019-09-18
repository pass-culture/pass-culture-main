import React from 'react'
import { shallow } from 'enzyme'

import SharePopin from '../SharePopin'

const dispatchMock = jest.fn()

describe('src | components | share | SharePopin', () => {
  it('should match the snapshot', () => {
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
    const wrapper = shallow(<SharePopin {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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
          const wrapper = shallow(<SharePopin {...props} />).dive()
          wrapper.find('button').simulate('click')
          const expected = {
            options: null,
            type: 'TOGGLE_SHARE_POPIN',
          }

          // then
          expect(dispatchMock).toHaveBeenCalledWith(expected)
        })
      })
    })
  })
})
