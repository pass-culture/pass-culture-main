import React from 'react'
import { shallow } from 'enzyme'

import Card from '../Card'

describe('src | components | pages | discovery | Deck | Card', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      handleClickRecommendation: jest.fn(),
      handleReadRecommendation: jest.fn(),
      match: { params: {} },
      position: 'position',
      width: 500,
    }

    // when
    const wrapper = shallow(<Card {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('background Color', () => {
      it('should render black', () => {
        // given
        const props = {
          handleClickRecommendation: jest.fn(),
          handleReadRecommendation: jest.fn(),
          match: { params: {} },
          position: 'position',
          width: 500,
        }

        // when
        const wrapper = shallow(<Card {...props} />)

        // then
        expect(wrapper.props().style.backgroundColor).toStrictEqual('black')
      })
    })
  })
})
