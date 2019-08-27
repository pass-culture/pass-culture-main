import { shallow } from 'enzyme'
import React from 'react'

import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyFavoriteContainer from '../MyFavorite/MyFavoriteContainer'
import MyFavorites from '../MyFavorites'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import NoItems from '../../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

describe('src | components | pages | my-favorites | MyFavorites', () => {
  let props

  beforeEach(() => {
    props = {
      deleteFavorites: jest.fn(),
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
      resetPageData: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<MyFavorites {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    describe('when there are no favorites', () => {
      it('should not render favorites', () => {
        // given
        props.myFavorites = []

        // when
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({ isLoading: false })

        // then
        const noItems = wrapper.find(NoItems)
        expect(noItems).toHaveLength(1)
        const myFavoriteContainer = wrapper.find(MyFavoriteContainer)
        expect(myFavoriteContainer).toHaveLength(0)
      })
    })

    describe('when click on "Modifier" button', () => {
      it('should render a list of simple div', () => {
        // given
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({ isLoading: false })

        // when
        wrapper.find('.mf-edit-btn').simulate('click')

        // then
        const header = wrapper.find(HeaderContainer)
        const deleteButton = wrapper.find('.mf-delete-btn')
        const editMode = wrapper.find('.mf-edit')
        const ul = wrapper.find('ul')
        const footer = wrapper.find(RelativeFooterContainer)
        expect(header).toHaveLength(1)
        expect(deleteButton).toHaveLength(1)
        expect(editMode).toHaveLength(1)
        expect(ul).toHaveLength(1)
        expect(footer).toHaveLength(1)
      })
    })

    describe('when click on "Terminer" button', () => {
      it('should render a list of Link', () => {
        // when
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({ isLoading: false })

        // then
        const header = wrapper.find(HeaderContainer)
        const deleteButton = wrapper.find('.mf-delete-btn')
        const doneMode = wrapper.find('.mf-done')
        const ul = wrapper.find('ul')
        const footer = wrapper.find(RelativeFooterContainer)
        expect(header).toHaveLength(1)
        expect(deleteButton).toHaveLength(0)
        expect(doneMode).toHaveLength(1)
        expect(ul).toHaveLength(1)
        expect(footer).toHaveLength(1)
      })
    })

    describe('when click on "Supprimer" button', () => {
      it('should remove two offer ids', () => {
        // given
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({ isEditMode: true, isLoading: false, offerIds: ['ME'] })

        // when
        wrapper.find('.mf-delete-btn').simulate('click')

        // then
        expect(props.deleteFavorites).toHaveBeenCalledWith(expect.any(Function), ['ME'])
      })
    })

    describe('when there is something wrong with API', () => {
      it('should render the Loader', () => {
        // when
        const wrapper = shallow(<MyFavorites {...props} />)

        // then
        const loaderContainer = wrapper.find(LoaderContainer)
        expect(loaderContainer).toHaveLength(1)
      })
    })

    describe('when unmount my component', () => {
      it('should reset the store', () => {
        // given
        const wrapper = shallow(<MyFavorites {...props} />)
        wrapper.setState({ isLoading: false })

        // when
        wrapper.unmount()

        // then
        expect(props.resetPageData).toHaveBeenCalledTimes(1)
      })
    })
  })
})
