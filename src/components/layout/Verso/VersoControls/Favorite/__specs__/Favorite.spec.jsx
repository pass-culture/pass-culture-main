import { shallow } from 'enzyme'
import React from 'react'

import Favorite from '../Favorite'

describe('src | components | layout | Verso | VersoControls | Favorite | Favorite', () => {
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

  describe('when the user can add to favorite', () => {
    it('should match the snapshot', () => {
      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the user can delete to favorite', () => {
    it('should match the snapshot', () => {
      // given
      props.isFavorite = false

      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the favorite functionnality is not implemented', () => {
    it('should match the snapshot', () => {
      // given
      props.isFeatureDisabled = true

      // when
      const wrapper = shallow(<Favorite {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the user click for adding to favorite', () => {
    it('should fill the heart', () => {
      // given
      const wrapper = shallow(<Favorite {...props} />)

      // when
      wrapper.find('button').simulate('click')

      // then
      expect(wrapper.find('i').props().title).toBe('Retirer des favoris')
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
      expect(wrapper.find('i').props().title).toBe('Ajouter aux favoris')
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
