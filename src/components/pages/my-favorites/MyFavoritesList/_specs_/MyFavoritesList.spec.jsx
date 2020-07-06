import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router'
import MyFavoritesList from '../../MyFavoritesList/MyFavoritesList'
import NoItems from '../../../../layout/NoItems/NoItems'
import TeaserContainer from '../../../../layout/Teaser/TeaserContainer'
import React from 'react'

describe('my Favorites', () => {
  let props

  beforeEach(() => {
    props = {
      persistDeleteFavorites: jest.fn(),
      loadMyFavorites: jest.fn(),
      myFavorites: [
        {
          id: 1,
          offerId: 'ME',
          offer: {
            id: 'ME',
            name: 'name',
          },
          mediationId: 'FA',
          mediation: {
            id: 'FA',
            thumbUrl: 'thumbUrl',
          },
        },
        {
          id: 2,
          offerId: 'ME2',
          offer: {
            id: 'ME2',
            name: 'name',
          },
          mediationId: 'FA2',
          mediation: {
            id: 'FA2',
            thumbUrl: 'thumbUrl',
          },
        },
      ],
    }
  })

  describe('when there are no favorites', () => {
    it('should display a button that redirects to discovery page', () => {
      // given
      props.myFavorites = []
      props.hasNoFavorite = true

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
      // given
      props.myFavorites = []
      props.hasNoFavorite = true

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
      // given
      props.myFavorites = []

      // when
      const wrapper = shallow(<MyFavoritesList {...props} />)

      // then
      const noItems = wrapper.find(NoItems)
      expect(noItems).toHaveLength(1)
      const myFavoriteContainer = wrapper.find(TeaserContainer)
      expect(myFavoriteContainer).toHaveLength(0)
    })
  })

  describe('when click on "Modifier" button', () => {
    it('should render a list of deletable favorites', () => {
      // given
      const wrapper = shallow(<MyFavoritesList {...props} />)

      // when
      wrapper.find('.mf-edit-btn').simulate('click')

      // then
      const deleteButton = wrapper.find('.mf-delete-btn')
      const editMode = wrapper.find('.mf-edit')
      const ul = wrapper.find('ul')
      expect(deleteButton).toHaveLength(1)
      expect(editMode).toHaveLength(1)
      expect(ul).toHaveLength(1)
    })
  })

  describe('when click on "Terminer" button', () => {
    it('should render a list of Link', () => {
      // when
      const wrapper = shallow(<MyFavoritesList {...props} />)

      // then
      const deleteButton = wrapper.find('.mf-delete-btn')
      const doneMode = wrapper.find('.mf-done')
      const ul = wrapper.find('ul')
      expect(deleteButton).toHaveLength(0)
      expect(doneMode).toHaveLength(1)
      expect(ul).toHaveLength(1)
    })
  })
})
