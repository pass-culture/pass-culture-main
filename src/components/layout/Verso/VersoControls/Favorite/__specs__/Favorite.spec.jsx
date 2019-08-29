import { shallow } from 'enzyme'
import React from 'react'

import Favorite from '../Favorite'

describe('src | components | verso | verso-controls | favorite | Favorite', () => {
  let props

  beforeEach(() => {
    props = {
      handleFavorite: jest.fn(),
      isFavorite: true,
      isFeatureDisabled: false,
      loadFavorites: jest.fn(),
      offerId: 'AE',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Favorite {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should load favorites', () => {
      // when
      shallow(<Favorite {...props} />)

      // then
      expect(props.loadFavorites).toHaveBeenCalledTimes(1)
    })

    it('should display icon to remove to favorite', () => {
      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      const icon = wrapper.find('i').props()
      expect(icon.title).toBe('Retirer des favoris')
      expect(icon.className).toBe('font-icon icon-ico-like-on')
    })

    it('should display icon to add to favorites', () => {
      // given
      props.isFavorite = false

      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      const icon = wrapper.find('i').props()
      expect(icon.title).toBe('Ajouter aux favoris')
      expect(icon.className).toBe('font-icon icon-ico-like')
    })
  })
})
