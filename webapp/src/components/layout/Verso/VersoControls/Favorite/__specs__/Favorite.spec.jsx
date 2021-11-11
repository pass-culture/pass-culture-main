import { shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'

import Icon from '../../../../../layout/Icon/Icon'
import Favorite from '../Favorite'

describe('src | components | Favorite', () => {
  let props

  beforeEach(() => {
    const history = createMemoryHistory()
    props = {
      handleFavorite: jest.fn(),
      history,
      isFavorite: true,
      loadFavorites: jest.fn(),
      offerId: 'AE',
      trackAddToFavoritesFromBooking: jest.fn(),
      trackAddToFavoritesFromHome: jest.fn(),
      trackAddToFavoritesFromOfferLink: jest.fn(),
      trackAddToFavoritesFromSearch: jest.fn(),
    }
  })

  describe('when the user click for deleting to favorite', () => {
    it.each`
      pathname                     | params
      ${'accueil/details/AE'}      | ${{ moduleName: 'Nom du module' }}
      ${'offre/details/AE'}        | ${{}}
      ${'reservations/details/AE'} | ${{}}
      ${'recherche/details/AE'}    | ${{}}
    `('it should not call tracking on $pathname', ({ pathname, params }) => {
      // given
      props.isFavorite = true
      props.history.push(pathname, params)
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Retirer des favoris')

      // when
      wrapper.find('button').simulate('click')

      // The tracking functions are not called
      expect(props.trackAddToFavoritesFromBooking).not.toHaveBeenCalled()
      expect(props.trackAddToFavoritesFromHome).not.toHaveBeenCalled()
      expect(props.trackAddToFavoritesFromOfferLink).not.toHaveBeenCalled()
      expect(props.trackAddToFavoritesFromSearch).not.toHaveBeenCalled()
    })
  })

  describe('when the user click for adding to favorite', () => {
    it('should called tracking if coming from home page', () => {
      // given
      props.isFavorite = false
      props.history.push('accueil/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromHome).toHaveBeenCalledWith('Nom du module', 'AE')
    })

    it('should not call AddToFavoritesFromHome on offer page', () => {
      // given
      props.isFavorite = false
      props.history.push('offre/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromHome).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromHome on search page', () => {
      // given
      props.isFavorite = false
      props.history.push('recherche/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromHome).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromHome on booking page', () => {
      // given
      props.isFavorite = false
      props.history.push('reservations/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromHome).not.toHaveBeenCalled()
    })

    it('should called tracking if coming from offer page', () => {
      // given
      props.isFavorite = false
      props.history.push('offre/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromOfferLink).toHaveBeenCalledWith('AE')
    })

    it('should not call AddToFavoritesFromOfferLink on home page', () => {
      // given
      props.isFavorite = false
      props.history.push('accueil/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromOfferLink).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromOfferLink on search page', () => {
      // given
      props.isFavorite = false
      props.history.push('recherche/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromOfferLink).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromOfferLink on booking page', () => {
      // given
      props.isFavorite = false
      props.history.push('reservations/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromOfferLink).not.toHaveBeenCalled()
    })
    it('should called tracking if coming from booking page', () => {
      // given
      props.isFavorite = false
      props.history.push('reservations/details/AE')
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromBooking).toHaveBeenCalledWith('AE')
    })

    it('should not call AddToFavoritesFromBooking on home page', () => {
      // given
      props.isFavorite = false
      props.history.push('accueil/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromBooking).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromBooking on search page', () => {
      // given
      props.isFavorite = false
      props.history.push('recherche/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromBooking).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromBooking on offer page', () => {
      // given
      props.isFavorite = false
      props.history.push('offre/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromBooking).not.toHaveBeenCalled()
    })

    it('should called tracking if coming from search page', () => {
      // given
      props.isFavorite = false
      props.history.push('recherche/details/AE')
      const wrapper = shallow(<Favorite {...props} />)
      expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromSearch).toHaveBeenCalledWith('AE')
    })

    it('should not call AddToFavoritesFromSearch on home page', () => {
      // given
      props.isFavorite = false
      props.history.push('accueil/details/AE', { moduleName: 'Nom du module' })
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromSearch).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromSearch on booking page', () => {
      // given
      props.isFavorite = false
      props.history.push('reservations/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromSearch).not.toHaveBeenCalled()
    })

    it('should not call AddToFavoritesFromSearch on offer page', () => {
      // given
      props.isFavorite = false
      props.history.push('offre/details/AE')
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(props.trackAddToFavoritesFromSearch).not.toHaveBeenCalled()
    })
  })

  describe('when the user click on the button', () => {
    it('should be disabled until the API responds', () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.find('button').props().disabled).toBe(true)
    })
  })
})
