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
      history: {
        location: {
          pathname: 'accueil/details/AE',
          moduleName: 'Nom du module',
        },
      },
      trackAddToFavoritesFromHome: jest.fn(),
    }
  })

  describe('when the user click for deleting to favorite', () => {
    it('should not called tracking', async () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)
      const mockTrackAddToFavorite = jest
        .spyOn(props, 'trackAddToFavoritesFromHome')
        .mockImplementation(jest.fn())
      expect(wrapper.find(Icon).props().alt).toBe('Retirer des favoris')

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(mockTrackAddToFavorite).not.toHaveBeenCalled()
    })
  })

  describe('when the user click for adding to favorite', () => {
    it('should called tracking if coming from home page', () => {
      // given
      props.isFavorite = false
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

      const mockTrackAddToFavorite = jest
        .spyOn(props, 'trackAddToFavoritesFromHome')
        .mockImplementation(jest.fn())

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(mockTrackAddToFavorite).toHaveBeenCalledWith('Nom du module', 'AE')
    })

    it('should not called tracking if coming from home page', () => {
      // given
      props.isFavorite = false
      props.history.location.pathname = 'offre/details/AE'
      const wrapper = shallow(<Favorite {...props} />)

      const mockTrackAddToFavorite = jest
        .spyOn(props, 'trackAddToFavoritesFromHome')
        .mockImplementation(jest.fn())

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(mockTrackAddToFavorite).not.toHaveBeenCalledWith()
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
