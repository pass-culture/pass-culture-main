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
    it.each`
      pathname                     | params                             | home     | offre    | booking  | search   | args
      ${'accueil/details/AE'}      | ${{ moduleName: 'Nom du module' }} | ${true}  | ${false} | ${false} | ${false} | ${['Nom du module', 'AE']}
      ${'offre/details/AE'}        | ${{}}                              | ${false} | ${true}  | ${false} | ${false} | ${['AE']}
      ${'reservations/details/AE'} | ${{}}                              | ${false} | ${false} | ${true}  | ${false} | ${['AE']}
      ${'recherche/details/AE'}    | ${{}}                              | ${false} | ${false} | ${false} | ${true}  | ${['AE']}
    `(
      'it should call tracking home=$home | offre=$offre | booking=$booking | search=$search on $pathname',
      ({ pathname, params, home, offre, booking, search, args }) => {
        // given
        props.isFavorite = false
        props.history.push(pathname, params)
        const wrapper = shallow(<Favorite {...props} />)
        expect(wrapper.find(Icon).props().alt).toBe('Ajouter aux favoris')

        // when
        wrapper.find('button').simulate('click')

        // then: one of the tracking functions is called
        if (booking) expect(props.trackAddToFavoritesFromBooking).toHaveBeenCalledWith(...args)
        if (home) expect(props.trackAddToFavoritesFromHome).toHaveBeenCalledWith(...args)
        if (offre) expect(props.trackAddToFavoritesFromOfferLink).toHaveBeenCalledWith(...args)
        if (search) expect(props.trackAddToFavoritesFromSearch).toHaveBeenCalledWith(...args)

        // The other functions are not called
        if (!booking) expect(props.trackAddToFavoritesFromBooking).not.toHaveBeenCalled()
        if (!home) expect(props.trackAddToFavoritesFromHome).not.toHaveBeenCalled()
        if (!offre) expect(props.trackAddToFavoritesFromOfferLink).not.toHaveBeenCalled()
        if (!search) expect(props.trackAddToFavoritesFromSearch).not.toHaveBeenCalled()
      }
    )
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
