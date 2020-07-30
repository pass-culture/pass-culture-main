import { shallow } from 'enzyme'
import React from 'react'

import Icon from '../../../../../layout/Icon/Icon'
import Favorite from '../Favorite'

describe('src | components | Favorite', () => {
  let props

  beforeEach(() => {
    props = {
      handleFavorite: jest.fn(),
      isFavorite: true,
      loadFavorites: jest.fn(),
      offerId: 'AE',
    }
  })

  describe('when the user click for adding to favorite', () => {
    it('should fill the heart', () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.find(Icon).props().alt).toBe('Retirer des favoris')
    })
  })

  describe('when the user click for deleting to favorite', () => {
    it('should empty the heart', () => {
      // given
      props.isFavorite = false
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')
    })
  })

  describe('when the user click on the button', () => {
    it('should disabled it until the API responde', () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.find('button').props().disabled).toBe(true)
    })
  })
})
