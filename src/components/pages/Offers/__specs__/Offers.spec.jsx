import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter, Router } from 'react-router'
import { NavLink } from 'react-router-dom'

import * as usersSelectors from '../../../../selectors/data/usersSelectors'
import { getStubStore } from '../../../../utils/stubStore'
import OfferItem from '../OfferItem/OfferItemContainer'
import Offers, { createLinkToOfferCreation } from '../Offers'

describe('src | components | pages | Offers | Offers', () => {
  let change
  let parse
  let props
  let currentUser

  beforeEach(() => {
    change = jest.fn()
    parse = () => ({})
    currentUser = { isAdmin: false }

    props = {
      closeNotification: jest.fn(),
      currentUser,
      handleOnActivateAllVenueOffersClick: jest.fn(),
      handleOnDeactivateAllVenueOffersClick: jest.fn(),
      loadOffers: jest.fn(),
      loadTypes: jest.fn(),
      location: {
        search: 'offres?lieu=AQ&structure=A4',
      },
      offers: [],
      query: {
        change,
        parse,
      },
      resetLoadedOffers: jest.fn(),
      types: [],
      venue: {},
    }
  })

  describe('render', () => {
    describe('when arriving on index page', () => {
      it('should list all offers', () => {
        // given
        const store = getStubStore({
          data: (
            state = {
              offerers: [],
              users: [{ publicName: 'User', id: 'EY' }],
            }
          ) => state,
          modal: (
            state = {
              config: {},
            }
          ) => state,
        })

        // when
        mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        // then
        expect(props.loadOffers).toHaveBeenCalledWith({
          apiPath: '/offers?',
          handleSuccess: expect.any(Function),
          handleFail: expect.any(Function),
          resolve: expect.any(Function),
        })
      })

      it('should display column titles when offers are returned', () => {
        // Given
        const store = getStubStore({
          data: (
            state = {
              offerers: [],
              users: [{ publicName: 'User', id: 'EY' }],
              venues: [{ id: 'JI', name: 'Venue' }],
            }
          ) => state,
          modal: (
            state = {
              config: {},
            }
          ) => state,
        })

        props.offers = [{ id: 'KE', availabilityMessage: 'Pas de stock', venueId: 'JI' }]

        // When
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        // Then
        const venueColumn = wrapper.find({ children: 'Lieu' })
        const stockColumn = wrapper.find({ children: 'Stock' })
        expect(venueColumn).toHaveLength(1)
        expect(stockColumn).toHaveLength(1)
      })

      it('should not display column titles when no offers are returned', () => {
        // Given
        const store = getStubStore({
          data: (
            state = {
              offerers: [],
              users: [{ publicName: 'User', id: 'EY' }],
              venues: [{ id: 'JI', name: 'Venue' }],
            }
          ) => state,
          modal: (
            state = {
              config: {},
            }
          ) => state,
        })

        props.offers = []

        // When
        const wrapper = mount(
          <Provider store={store}>
            <MemoryRouter>
              <Offers {...props} />
            </MemoryRouter>
          </Provider>
        )

        // Then
        const venueColumn = wrapper.find({ children: 'Lieu' })
        const stockColumn = wrapper.find({ children: 'Stock' })
        expect(venueColumn).toHaveLength(0)
        expect(stockColumn).toHaveLength(0)
      })
    })

    describe('offerer filter button', () => {
      it('should be displayed when offerer is given', () => {
        // given
        props.offerer = {
          name: 'Scope La Brique',
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.offerer-filter')
        // then
        expect(offererButton).toHaveLength(1)
        expect(offererButton.text()).toBe('Structure : Scope La Brique<Icon />')
      })

      it('should not be displayed when offerer is given', () => {
        // given
        props.offerer = null

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.offerer-filter')

        // then
        expect(offererButton).toHaveLength(0)
      })

      it('should update url and remove offerer filter', () => {
        // given
        props.offerer = {
          name: 'Scope La Brique',
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.offerer-filter')
        offererButton.simulate('click')

        // then
        expect(props.query.change).toHaveBeenCalledWith({
          page: null,
          structure: null,
        })
      })
    })

    describe('venue filter', () => {
      it('should be displayed when venue is given', () => {
        // given
        props.venue = {
          name: 'La verbeuse',
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.venue-filter')
        // then
        expect(offererButton).toHaveLength(1)
        expect(offererButton.text()).toBe('Lieu : La verbeuse<Icon />')
      })

      it('should not be displayed when venue is given', () => {
        // given
        props.venue = null

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.venue-filter')

        // then
        expect(offererButton).toHaveLength(0)
      })

      it('should update url and remove venue filter', () => {
        // given
        props.venue = {
          name: 'La verbeuse',
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.venue-filter')
        offererButton.simulate('click')

        // then
        expect(props.query.change).toHaveBeenCalledWith({
          page: null,
          lieu: null,
        })
      })
    })

    describe('offerItem', () => {
      it('should render items corresponding to offers', () => {
        // given
        props.offers = [
          {
            id: 'M4',
            isActive: true,
            isEditable: true,
            isFullyBooked: false,
            isEvent: true,
            isThing: false,
            hasBookingLimitDatetimesPassed: false,
            name: 'My little offer',
            thumbUrl: '/my-fake-thumb',
          },
          {
            id: 'AE3',
            isActive: true,
            isEditable: true,
            isFullyBooked: true,
            isEvent: false,
            isThing: true,
            hasBookingLimitDatetimesPassed: false,
            name: 'My other offer',
            thumbUrl: '/my-other-fake-thumb',
          },
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offerItem = wrapper.find(OfferItem)

        // then
        expect(offerItem).toHaveLength(props.offers.length)
      })
    })

    describe('navLink to create offer', () => {
      describe('when user isAdmin', () => {
        it('should not display the link', () => {
          // given
          props.currentUser = {
            isAdmin: true,
          }

          // when
          const wrapper = shallow(<Offers {...props} />)
          const navLink = wrapper.find(NavLink)

          // then
          expect(navLink).toHaveLength(0)
        })
      })

      describe('when user is not admin', () => {
        it('should display a link to create an offer', () => {
          // given
          props.currentUser.isAdmin = false
          const store = getStubStore({
            data: (
              state = {
                offerers: [],
              }
            ) => state,
            modal: (
              state = {
                config: {},
              }
            ) => state,
          })
          const history = createMemoryHistory()
          jest
            .spyOn(usersSelectors, 'selectCurrentUser')
            .mockReturnValue({ currentUser: props.currentUser })
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Offers {...props} />
              </Router>
            </Provider>
          )
          const offerCreationLink = wrapper.find({ children: 'Créer une offre' })

          // when
          offerCreationLink.simulate('click', { button: 0 })

          // then
          expect(history.location.pathname + history.location.search).toStrictEqual(
            '/offres/creation'
          )
        })
      })

      describe('when structure (or offererId)', () => {
        it('should render link properly', () => {
          // given
          const store = getStubStore({
            data: (
              state = {
                offerers: [],
              }
            ) => state,
            modal: (
              state = {
                config: {},
              }
            ) => state,
          })
          const history = createMemoryHistory()
          jest
            .spyOn(usersSelectors, 'selectCurrentUser')
            .mockReturnValue({ currentUser: props.currentUser })
          jest.spyOn(props.query, 'parse').mockReturnValue({ structure: 'XY' })
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Offers {...props} />
              </Router>
            </Provider>
          )
          const offerCreationLink = wrapper.find({ children: 'Créer une offre' })

          // when
          offerCreationLink.simulate('click', { button: 0 })

          // then
          expect(history.location.pathname + history.location.search).toStrictEqual(
            '/offres/creation?structure=XY'
          )
        })
      })
      describe('when lieu or (VenueId)', () => {
        it('should render link properly', () => {
          // given
          const store = getStubStore({
            data: (
              state = {
                offerers: [],
              }
            ) => state,
            modal: (
              state = {
                config: {},
              }
            ) => state,
          })
          const history = createMemoryHistory()
          jest
            .spyOn(usersSelectors, 'selectCurrentUser')
            .mockReturnValue({ currentUser: props.currentUser })
          jest.spyOn(props.query, 'parse').mockReturnValue({ lieu: 'G6' })
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Offers {...props} />
              </Router>
            </Provider>
          )
          const offerCreationLink = wrapper.find({ children: 'Créer une offre' })

          // when
          offerCreationLink.simulate('click', { button: 0 })

          // then
          expect(history.location.pathname + history.location.search).toStrictEqual(
            '/offres/creation?lieu=G6'
          )
        })
      })
    })

    describe('deactivate all offers from a venue', () => {
      it('should be displayed when offers and venue are given', () => {
        // given
        props.venue = {
          name: 'Le biennommé',
        }
        props.offers = [
          {
            id: 'N9',
          },
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const deactivateButton = wrapper.find('button.deactivate')

        // then
        expect(deactivateButton).toHaveLength(1)
        expect(deactivateButton.text()).toBe('Désactiver toutes les offres')
      })

      it('should not be displayed when offers or venue is missing', () => {
        // given
        props.venue = null
        props.offers = [
          {
            id: 'N9',
          },
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const deactivateButton = wrapper.find('button.deactivate')

        // then
        expect(deactivateButton).toHaveLength(0)
      })

      it('should send a request to api when clicked', () => {
        // given
        props.venue = {
          id: 'GY',
          name: 'Le biennommé',
        }
        props.offers = [
          {
            id: 'N9',
          },
        ]
        // given
        const wrapper = shallow(<Offers {...props} />)

        // when
        const deactivateButton = wrapper.find('button.deactivate')
        deactivateButton.simulate('click')

        // then
        expect(props.handleOnDeactivateAllVenueOffersClick).toHaveBeenCalledWith({
          id: 'GY',
          name: 'Le biennommé',
        })
      })
    })

    describe('activate all offers from a venue', () => {
      it('should be displayed when offers and venue are given', () => {
        // given
        props.venue = {
          name: 'Le biennommé',
        }
        props.offers = [
          {
            id: 'N9',
          },
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const activateButton = wrapper.find('button.activate')
        // then
        expect(activateButton).toHaveLength(1)
        expect(activateButton.text()).toBe('Activer toutes les offres')
      })

      it('should not be displayed when offers or venue is missing', () => {
        // given
        props.venue = null
        props.offers = [
          {
            id: 'N9',
          },
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const activateButton = wrapper.find('button.activate')

        // then
        expect(activateButton).toHaveLength(0)
      })

      it('should send a request to api when clicked', () => {
        // given
        props.venue = {
          id: 'GY',
          name: 'Le biennommé',
        }
        props.offers = [
          {
            id: 'N9',
          },
        ]
        // given
        const wrapper = shallow(<Offers {...props} />)

        // when
        const activateButton = wrapper.find('button.activate')
        activateButton.simulate('click')

        // then
        expect(props.handleOnActivateAllVenueOffersClick).toHaveBeenCalledWith({
          id: 'GY',
          name: 'Le biennommé',
        })
      })
    })

    describe('should render search offers form', () => {
      describe('when keywords is not an empty string', () => {
        it('should change query', () => {
          // given
          const store = getStubStore({
            data: (
              state = {
                offerers: [],
                users: [{ publicName: 'User', id: 'EY' }],
              }
            ) => state,
            modal: (
              state = {
                config: {},
              }
            ) => state,
          })

          const wrapper = mount(
            <Provider store={store}>
              <MemoryRouter>
                <Offers {...props} />
              </MemoryRouter>
            </Provider>
          )

          // when
          const searchInput = wrapper.find(
            'input[placeholder="Saisissez un ou plusieurs mots complets"]'
          )
          const launchSearchButton = wrapper.find('form')
          searchInput.invoke('onChange')({ target: { value: 'AnyWord' } })
          launchSearchButton.invoke('onSubmit')({ preventDefault: jest.fn() })

          // then
          expect(change.mock.calls[0][0]).toStrictEqual({
            'mots-cles': 'AnyWord',
            page: null,
          })
          change.mockClear()
        })
      })

      describe('when keywords is an empty string', () => {
        it('should change query with mots-clés setted to null on form submit', () => {
          // given
          const wrapper = shallow(<Offers {...props} />)
          const eventEmptyWord = Object.assign(jest.fn(), {
            preventDefault: () => {},
            target: {
              elements: {
                search: {
                  value: '',
                },
              },
            },
          })

          // when
          wrapper.instance().handleOnSubmit(eventEmptyWord)
          // then
          expect(change.mock.calls[0][0]).toStrictEqual({
            'mots-cles': null,
            page: null,
          })
          change.mockClear()
        })
      })
    })

    describe('when leaving page', () => {
      it('should close offers activation / deactivation notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: {
            tag: 'offers-activation',
          },
        }
        const wrapper = shallow(<Offers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).toHaveBeenCalledWith()
      })

      it('should not fail on null notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: null,
        }
        const wrapper = shallow(<Offers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).not.toHaveBeenCalledWith()
      })
    })
  })

  describe('createLinkToOfferCreation', () => {
    it('should create link when venue only is in path', () => {
      // given
      const venueId = 'TF'
      const offererId = undefined

      // when
      const result = createLinkToOfferCreation(venueId, offererId)

      // then
      expect(result).toStrictEqual('/offres/creation?lieu=TF')
    })

    it('should create link when offerer only is in path', () => {
      // given
      const venueId = undefined
      const offererId = 'TF'

      // when
      const result = createLinkToOfferCreation(venueId, offererId)

      // then
      expect(result).toStrictEqual('/offres/creation?structure=TF')
    })

    it('should create link when offerer and venue are in path', () => {
      // given
      const venueId = '7X'
      const offererId = 'TF'

      // when
      const result = createLinkToOfferCreation(venueId, offererId)

      // then
      expect(result).toStrictEqual('/offres/creation?structure=TF&lieu=7X')
    })
  })
})
