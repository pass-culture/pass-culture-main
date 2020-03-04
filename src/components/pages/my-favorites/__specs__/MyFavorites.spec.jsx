import configureStore from 'redux-mock-store'
import { createMemoryHistory } from 'history'
import { mount, shallow } from 'enzyme'
import { Provider } from 'react-redux'
import React from 'react'
import { Router } from 'react-router-dom'
import thunk from 'redux-thunk'

import Booking from '../../../layout/Booking/Booking'
import LoaderContainer from '../../../layout/Loader/LoaderContainer'
import MyFavorites from '../MyFavorites'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import NoItems from '../../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'
import state from '../../../../mocks/state'
import TeaserContainer from '../../../layout/Teaser/TeaserContainer'

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
        const myFavoriteContainer = wrapper.find(TeaserContainer)
        expect(myFavoriteContainer).toHaveLength(0)
      })
    })

    describe('when click on "Modifier" button', () => {
      it('should render a list of deletable favorites', () => {
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
      it('should remove one offer id', () => {
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

    describe('when on details page I can initiate booking', () => {
      it('should open booking component with offerId and mediationId on url', () => {
        // given
        const buildStore = configureStore([thunk])
        const store = buildStore(state)
        const history = createMemoryHistory()
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
          myFavorites: [
            {
              id: 1,
              offerId: 'AM3A',
              offer: {
                id: 'AM3A',
                name: 'name',
              },
              mediationId: 'B4',
              mediation: {
                id: 'B4',
                thumbUrl: 'thumbUrl',
              },
            },
          ],
        }
        history.push('/favoris/details/AM3A/B4/reservation')

        // when
        const wrapper = mount(
          <Router history={history}>
            <Provider store={store}>
              <MyFavorites {...props} />
            </Provider>
          </Router>
        )
        const myFavorites = wrapper.find(MyFavorites)
        myFavorites.setState({ isLoading: false })

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })

      it('should open booking component with no mediationId on url', () => {
        // given
        const buildStore = configureStore([thunk])
        const store = buildStore(state)
        const history = createMemoryHistory()
        const props = {
          deleteFavorites: jest.fn(),
          loadMyFavorites: jest.fn(),
          myFavorites: [
            {
              id: 1,
              offerId: 'AM3A',
              offer: {
                id: 'AM3A',
                name: 'name',
              },
            },
          ],
        }

        // when
        history.push('/favoris/details/AM3A/vide/reservation')
        const wrapper = mount(
          <Router history={history}>
            <Provider store={store}>
              <MyFavorites {...props} />
            </Provider>
          </Router>
        )
        const myFavorites = wrapper.find(MyFavorites)
        myFavorites.setState({ isLoading: false })

        // then
        const booking = wrapper.find(Booking)
        expect(booking.isEmptyRender()).toBe(false)
      })
    })
  })
})
