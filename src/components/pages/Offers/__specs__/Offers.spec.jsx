import React from 'react'
import { shallow } from 'enzyme'
import { NavLink } from 'react-router-dom'
import { resolveIsNew } from 'pass-culture-shared'


import Offers from '../Offers'
import OfferItem from '../OfferItem/OfferItemContainer'
import mockedOffers from './offersMock'

describe('src | components | pages | Offers | Offers', () => {
  let change
  let dispatch
  let parse
  let props
  let currentUser

  beforeEach(() => {
    change = jest.fn()
    dispatch = jest.fn()
    parse = () => ({})
    currentUser = { isAdmin: false }

    props = {
      currentUser,
      dispatch,
      offers: [],
      location: {
        pathname: '/offres',
        search: 'offres?lieu=AQ&structure=A4'
      },
      pagination: {
        apiQuery: {
          keywords: null,
          offererId: null,
          orderBy: 'offer.id+desc',
          venueId: null,
        },
      },
      query: {
        change,
        parse,
      },
      types: [],
      venue: {}
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Offers {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
    dispatch.mockClear()
    change.mockClear()
  })

  describe('render', () => {
    describe('when arriving on index page', () => {
      it('should list all offers', () => {
        // given
        const expected = {
          hasMore: false,
          isLoading: true,
        }

        // when
        const wrapper = shallow(<Offers {...props} />)

        // then
        expect(wrapper.state()).toStrictEqual(expected)
        dispatch.mockClear()
        change.mockClear()
      })
    })

    describe('offerer filter button', () => {
      it('should be displayed when offerer is given', () => {
        // given
        props.offerer = {
          name: "Scope La Brique"
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.offerer-filter')
        // then
        expect(offererButton).toHaveLength(1)
        expect(offererButton.text()).toBe("Structure : Scope La Brique<Icon />")
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
          name: "Scope La Brique"
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.offerer-filter')
        offererButton.simulate('click')
        const expected = {
          "page": null,
          "structure": null
        }

        // then
        expect(props.query.change).toHaveBeenCalledWith(expected)
      })
    })

    describe('venue filter', () => {
      it('should be displayed when venue is given', () => {
        // given
        props.venue = {
          name: "La verbeuse"
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.venue-filter')
        // then
        expect(offererButton).toHaveLength(1)
        expect(offererButton.text()).toBe("Lieu : La verbeuse<Icon />")
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
          name: "La verbeuse"
        }

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offererButton = wrapper.find('button.venue-filter')
        offererButton.simulate('click')
        const expected = {
          "page": null,
          "lieu": null
        }

        // then
        expect(props.query.change).toHaveBeenCalledWith(expected)
      })
    })

    describe('offerItem', () => {
      it('should render items corresponding to offers', () => {
        // given
        props.offers = mockedOffers

        // when
        const wrapper = shallow(<Offers {...props} />)
        const offerItem = wrapper.find(OfferItem)

        // then
        expect(offerItem).toHaveLength(mockedOffers.length)
      })
    })

    describe('navLink to create offer', () => {
      describe('when user isAdmin', () => {
        it('should not display NavLink', () => {
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
      describe('when structure (or offererId)', () => {
        it('should render link properly', () => {
          // given
          props.query.parse = () => ({ structure: 'XY' })

          // when
          const wrapper = shallow(<Offers {...props} />)
          const navLink = wrapper.find(NavLink)
          const span = wrapper.find(NavLink).find('span').at(1)

          // then
          expect(navLink).toHaveLength(1)
          expect(navLink.props().to).toStrictEqual('/offres/creation?structure=XY')
          expect(span.text()).toBe("Créer une offre")

        })
      })
      describe('when lieu or (VenueId)', () => {
        it('should render link properly', () => {
          // given
          props.currentUser = {
            isAdmin: false,
          }
          props.query.parse = () => ({ lieu: 'G6' })

          // when
          const wrapper = shallow(<Offers {...props} />)
          const navLink = wrapper.find(NavLink)
          const span = wrapper.find(NavLink).find('span').at(1)

          // then
          expect(navLink).toHaveLength(1)
          expect(navLink.props().to).toStrictEqual('/offres/creation?lieu=G6')
          expect(span.text()).toBe("Créer une offre")
        })
      })
    })

    describe('deactivate all offers from a venue', () => {
      it('should be displayed when offers and venue are given', () => {
        // given
        props.venue = {
          name: 'Le biennommé'
        }
        props.offers = [{
          id: "N9"
          }
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const deactivateButton = wrapper.find('button.deactivate')

        // then
        expect(deactivateButton).toHaveLength(1)
        expect(deactivateButton.text()).toBe("Désactiver toutes les offres")
      })

      it('should not be displayed when offers or venue is missing', () => {
        // given
        props.venue = null
        props.offers = [{
          id: "N9"
          }
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
          name: 'Le biennommé'
        }
        props.offers = [{
          id: "N9"
          }
        ]
        // given
        const wrapper = shallow(<Offers {...props} />)

        // when
        const deactivateButton = wrapper.find('button.deactivate')
        deactivateButton.simulate('click')

        // then
        const expected = {
          'config':
          { 'apiPath': '/venues/GY/offers/deactivate',
            'handleSuccess': undefined,
            'method': 'PUT',
            'stateKey': 'offers',
          },
          'type': 'REQUEST_DATA_PUT_OFFERS'
        }
        expect(props.dispatch).toHaveBeenCalledWith(expected)
      })
    })

    describe('activate all offers from a venue', () => {
      it('should be displayed when offers and venue are given', () => {
        // given
        props.venue = {
          name: 'Le biennommé'
        }
        props.offers = [{
          id: "N9"
          }
        ]

        // when
        const wrapper = shallow(<Offers {...props} />)
        const activateButton = wrapper.find('button.activate')
        // then
        expect(activateButton).toHaveLength(1)
        expect(activateButton.text()).toBe("Activer toutes les offres")
      })

      it('should not be displayed when offers or venue is missing', () => {
        // given
        props.venue = null
        props.offers = [{
          id: "N9"
          }
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
          name: 'Le biennommé'
        }
        props.offers = [{
          id: "N9"
          }
        ]
        // given
        const wrapper = shallow(<Offers {...props} />)

        // when
        const activateButton = wrapper.find('button.activate')
        activateButton.simulate('click')

        // then
        const expected = {
          config: {
            apiPath: '/venues/GY/offers/activate',
            handleSuccess: undefined,
            method: 'PUT',
            stateKey: 'offers',
          },
          type: 'REQUEST_DATA_PUT_OFFERS'
        }
        expect(props.dispatch).toHaveBeenCalledWith(expected)
      })
    })

    describe('should render search offers form', () => {
      describe('when keywords is not an empty string', () => {
        const event = Object.assign(jest.fn(), {
          preventDefault: () => {},
          target: {
            elements: {
              search: {
                value: 'AnyWord',
              },
            },
          },
        })
        it('should update state with isLoading to true on form submit', () => {
          // given
          const wrapper = shallow(<Offers {...props} />)

          // when
          wrapper.instance().handleOnSubmit(event)
          const expected = {
            hasMore: false,
            isLoading: true,
          }

          // then
          expect(wrapper.state()).toStrictEqual(expected)
        })

        it('should dispatch assignData with good params on form submit', () => {
          // given
          const wrapper = shallow(<Offers {...props} />)

          // when
          wrapper.instance().handleOnSubmit(event)

          const expected = {
            patch: {
              offers: [],
            },
            type: 'ASSIGN_DATA',
          }

          // then
          expect(dispatch.mock.calls[0][0]).toStrictEqual(expected)
          dispatch.mockClear()
        })

        it('should change query', () => {
          // given
          const wrapper = shallow(<Offers {...props} />)

          // when
          wrapper.instance().handleOnSubmit(event)
          const expected = {
            'mots-cles': 'AnyWord',
            page: null,
          }

          // then
          expect(change.mock.calls[0][0]).toStrictEqual(expected)
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
          const expected = {
            'mots-cles': null,
            page: null,
          }

          // then
          expect(change.mock.calls[0][0]).toStrictEqual(expected)
          change.mockClear()
        })
      })
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      it('should dispatch assignData when component is constructed', () => {
        // when
        shallow(<Offers {...props} />)
        const expectedAssignData = {
          patch: {
            offers: [],
          },
          type: 'ASSIGN_DATA',
        }

        // then
        expect(dispatch.mock.calls[0][0]).toStrictEqual(expectedAssignData)
        dispatch.mockClear()
        change.mockClear()
      })
    })

    describe('componentDidMount', () => {
      it('should dispatch handleRequestData when there is no pagination', () => {
        // when
        const wrapper = shallow(<Offers {...props} />)
        wrapper.instance().componentDidMount()
        const expected = {
          config: {
            apiPath: '/types',
            method: 'GET',
          },
          type: 'REQUEST_DATA_GET_/TYPES',
        }

        // then
        expect(dispatch.mock.calls[3][0]).toStrictEqual(expected)
      })

      it('should change query when there is pagination', () => {
        // given
        props.query.parse =  () => ({'page': '2'})

        // when
        const wrapper = shallow(<Offers {...props} />)
        wrapper.instance().componentDidMount()
        const expected = {'page': null}

        // then
        expect(props.query.change).toHaveBeenCalledWith(expected)
        dispatch.mockClear()
    })

    describe('handleSubmitRequestSuccess', () => {
      it('sould dispatch a succes notificationMessage', () => {
        // given
        const wrapper = shallow(<Offers {...props} />)

        // when
        wrapper.instance().handleSubmitRequestSuccess('Fake message')

        // then
        const expected = {
          'patch': {
            'text': 'Fake message',
            'type': 'success'
          },
          'type': 'SHOW_NOTIFICATION'
        }

        expect(props.dispatch).toHaveBeenCalledWith(expected)
      })
    })

    describe('componentDidUpdate', () => {
      describe('when location has change', () => {
        it('should dispatch assignData when component is rendered', () => {
          // given
          props.query.parse = () => ({lieu: 'TY'})
          props.location =  {
            pathname: '/offres',
            search: 'offres?lieu=AQ',
          }
          const prevProps = props

          // when
          const wrapper = shallow(<Offers {...props} />)
          wrapper.instance().componentDidUpdate(prevProps)

          const resolve = (datum) => resolveIsNew(datum, 'dateCreated', comparedTo)
          const expected = { hasMore: false, isLoading: true }
          const expectedAssignData = {
              config: {
                apiPath: "/offers?venueId=TY",
                handleFail: expect.any(Function),
                handleSuccess: expect.any(Function),
                method: 'GET',
                normalizer: {
                  mediations: 'mediations',
                  product: {
                    normalizer: {
                      offers  : 'offers'
                    },
                  stateKey: 'products'
                  },
                  stocks: 'stocks',
                  venue: {
                    normalizer: {
                      managingOfferer: 'offerers'
                    },
                  stateKey: 'venues'
                }
              },
              resolve
                },
                type: 'REQUEST_DATA_GET_/OFFERS?VENUEID=TY'}

          // then
          expect(dispatch.mock.calls[2][0].config.apiPath).toStrictEqual(expectedAssignData.config.apiPath)
          expect(dispatch.mock.calls[2][0].config.method).toStrictEqual(expectedAssignData.config.method)
          expect(dispatch.mock.calls[2][0].config.type).toStrictEqual(expectedAssignData.config.type)
          expect(wrapper.state()).toStrictEqual(expected)

          dispatch.mockClear()
        })
      })
    })
    })
  })
})
