import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { ApiError } from '../../../../layout/ErrorBoundaries/ErrorsPage/ApiError'
import LoaderContainer from '../../../../layout/Loader/LoaderContainer'
import NoItems from '../../../../layout/NoItems/NoItems'
import TeaserContainer from '../../../../layout/Teaser/TeaserContainer'
import MyFavoritesList from '../../MyFavoritesList/MyFavoritesList'

describe('my Favorites', () => {
  let props

  beforeEach(() => {
    props = {
      loadMyFavorites: jest.fn(),
      myFavorites: [],
      persistDeleteFavorites: jest.fn(),
    }
  })

  describe('when data is fetching', () => {
    it('should display a loading screen', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/favoris']}>
          <MyFavoritesList {...props} />
        </MemoryRouter>
      )

      // then
      const loader = wrapper.find(LoaderContainer)
      expect(loader).toHaveLength(1)
    })
  })

  describe('when API fail', () => {
    it('should display only an error screen', () => {
      // given
      jest
        .spyOn(props, 'loadMyFavorites')
        .mockImplementation(fail => fail({}, { payload: { status: 500 } }))

      // when
      const wrapper = () =>
        mount(
          <MemoryRouter initialEntries={['/favoris']}>
            <MyFavoritesList {...props} />
          </MemoryRouter>
        )

      // then
      expect(wrapper).toThrow(ApiError)
    })
  })

  describe('when API succeed', () => {
    beforeEach(() => {
      jest.spyOn(props, 'loadMyFavorites').mockImplementation((fail, success) => success())
    })

    it('should display the title "Favoris"', () => {
      // when
      const wrapper = mount(
        <MemoryRouter initialEntries={['/favoris']}>
          <MyFavoritesList {...props} />
        </MemoryRouter>
      )

      // then
      const title = wrapper.find('h1').find({ children: 'Favoris' })
      expect(title).toHaveLength(1)
    })

    describe('when there are no favorites', () => {
      it('should display a button that redirects to discovery page', () => {
        // when
        const wrapper = mount(
          <MemoryRouter initialEntries={['/favoris']}>
            <MyFavoritesList {...props} />
          </MemoryRouter>
        )

        // then
        const redirectButton = wrapper.find('a')
        expect(redirectButton.text()).toBe('Lance-toi !')
        expect(redirectButton.prop('href')).toBe('/decouverte')
      })

      it('should display a description text', () => {
        // when
        const wrapper = mount(
          <MemoryRouter initialEntries={['/favoris']}>
            <MyFavoritesList {...props} />
          </MemoryRouter>
        )

        // then
        const descriptionText = wrapper.find({
          children: 'Dès que tu auras ajouté une offre à tes favoris, tu la retrouveras ici.',
        })
        expect(descriptionText).toHaveLength(1)
      })

      it('should not render favorites', () => {
        // when
        const wrapper = mount(
          <MemoryRouter initialEntries={['/favoris']}>
            <MyFavoritesList {...props} />
          </MemoryRouter>
        )

        // then
        const noItems = wrapper.find(NoItems)
        expect(noItems).toHaveLength(1)
        const myFavoriteContainer = wrapper.find(TeaserContainer)
        expect(myFavoriteContainer).toHaveLength(0)
      })
    })
  })
})
