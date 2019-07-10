import { shallow } from 'enzyme'
import React from 'react'

import Favorite from '../Favorite'

describe('src | components | verso | verso-controls | favorite | Favorite', () => {
  let props

  beforeEach(() => {
    props = {
      handleFavorite: jest.fn(),
      recommendation: {
        offer: {
          favorites: [],
        },
      },
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Favorite {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should display icon to remove to favorite', () => {
      // given
      props.recommendation.offer.favorites = [{}]

      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      const icon = wrapper.find('i').props()
      expect(icon.title).toBe('Retirer des favoris')
      expect(icon.className).toBe('font-icon icon-ico-like-on')
    })

    it('should display icon to add to favorites', () => {
      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      const icon = wrapper.find('i').props()
      expect(icon.title).toBe('Ajouter aux favoris')
      expect(icon.className).toBe('font-icon icon-ico-like')
    })

    it('should handle favorites when click on button', () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)
      const button = wrapper.find('button')

      // when
      button.simulate('click')

      // then
      expect(props.handleFavorite).toHaveBeenCalledWith(
        false,
        { offer: { favorites: [] } },
        expect.anything(Function)
      )
    })
  })
})
