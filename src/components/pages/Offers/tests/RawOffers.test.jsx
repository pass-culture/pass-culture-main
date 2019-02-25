import React from 'react'
import { shallow } from 'enzyme'
import { NavLink } from 'react-router-dom'

import RawOffers from '../RawOffers'
import OfferItem from '../OfferItem'
import mockedOffers from './offersMock'

const dispatchMock = jest.fn()
const queryChangeMock = jest.fn()
const initialProps = {
  dispatch: dispatchMock,
  offers: [],
  location: {
    pathname: '/offres',
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
    change: queryChangeMock,
    parse: () => ({ orderBy: 'offer.id desc' }),
  },
  search: '',
  types: [],
  user: {},
}

describe('src | components | pages | Offers | RawOffers', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<RawOffers {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
      dispatchMock.mockClear()
      queryChangeMock.mockClear()
    })
  })

  describe('render', () => {
    describe('when arriving on index page', () => {
      it('should list all offers', () => {
        // given
        const expected = {
          hasMore: false,
          isLoading: true,
          keywordsValue: undefined,
        }

        // when
        const wrapper = shallow(<RawOffers {...initialProps} />)

        // then
        expect(wrapper.state()).toEqual(expected)
        dispatchMock.mockClear()
        queryChangeMock.mockClear()
      })
    })
    describe('OfferItem', () => {
      it('should render items corresponding to offers', () => {
        // given
        initialProps.offers = mockedOffers

        // when
        const wrapper = shallow(<RawOffers {...initialProps} />)
        const offerItem = wrapper.find(OfferItem)

        // then
        expect(offerItem).toHaveLength(mockedOffers.length)
      })
    })
    describe('When offers showned for an offerer or a venue', () => {
      describe('NavLink to create offer', () => {
        describe('When user isAdmin', () => {
          it('should display NavLink', () => {
            // given
            initialProps.user = {
              isAdmin: true,
            }

            // when
            const wrapper = shallow(<RawOffers {...initialProps} />)
            const navLink = wrapper.find(NavLink)

            // then
            expect(navLink).toHaveLength(0)
          })
        })
        describe('When structure (or offererId)', () => {
          it('should render link properly', () => {
            // given
            initialProps.user = {
              isAdmin: false,
            }
            const parseMock = () => ({ structure: 'TEST' })
            initialProps.query.parse = parseMock

            // when
            const wrapper = shallow(<RawOffers {...initialProps} />)

            const navLink = wrapper.find(NavLink)

            // then
            expect(navLink).toHaveLength(1)
            expect(navLink.props().to).toEqual('/offres/nouveau?structure=TEST')
          })
        })
        describe('When lieu or (VenueId)', () => {
          it('should render link properly', () => {
            // given
            initialProps.user = {
              isAdmin: false,
            }
            const parseMock = () => ({ lieu: 'LIEU' })
            initialProps.query.parse = parseMock

            // when
            const wrapper = shallow(<RawOffers {...initialProps} />)

            const navLink = wrapper.find(NavLink)

            // then
            expect(navLink).toHaveLength(1)
            expect(navLink.props().to).toEqual('/offres/nouveau?lieu=LIEU')
          })
        })
      })
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      it('should dispatch assignData when component is constructed', () => {
        // when
        shallow(<RawOffers {...initialProps} />)
        const expectedAssignData = {
          patch: {
            offers: [],
          },
          type: 'ASSIGN_DATA',
        }

        // then
        expect(dispatchMock.mock.calls[0][0]).toEqual(expectedAssignData)
        dispatchMock.mockClear()
        queryChangeMock.mockClear()
      })
    })

    describe('componentDidMount', () => {
      describe('when there is pagination', () => {
        it.skip('should call query change with good params', () => {
          // given
          const parseMock = () => ({ page: 1 })
          initialProps.query.parse = parseMock
          initialProps.query.change = queryChangeMock

          // when
          const wrapper = shallow(<RawOffers {...initialProps} />)

          wrapper.instance().componentDidMount()

          // then
          expect(queryChangeMock.mock.call).toEqual({ page: null })
          queryChangeMock.mockClear()
        })
      })

      describe('when there is no pagination', () => {
        it('should dispatch handle RequestData', () => {
          // given
          const parseMock = () => ({
            keywords: 'océan',
            orderBy: 'offer.id desc',
          })
          initialProps.query.parse = parseMock

          // when
          const wrapper = shallow(<RawOffers {...initialProps} />)
          wrapper.instance().componentDidMount()
          const expected = {
            config: {},
            method: 'GET',
            path: 'types',
            type: 'REQUEST_DATA_GET_TYPES',
          }

          // then
          expect(dispatchMock.mock.calls[1][0]).toEqual(expected)
          dispatchMock.mockClear()
        })
      })
    })

    describe('componentDidUpdate', () => {
      describe('when location has change', () => {
        it('should dispatch assignData when component is rendered', () => {
          // given
          const prevProps = initialProps

          initialProps.location = {
            pathname: '/offres',
            search: '?orderBy=offer.id+desc',
          }

          // when
          const wrapper = shallow(<RawOffers {...initialProps} />)
          wrapper.instance().componentDidUpdate(prevProps)

          const expectedAssignData = {
            config: {},
            method: 'GET',
            path: 'types',
            type: 'REQUEST_DATA_GET_TYPES',
          }

          // the
          expect(dispatchMock.mock.calls[1][0]).toEqual(expectedAssignData)

          dispatchMock.mockClear()
        })
      })
    })

    describe('onSubmit', () => {
      // when
      const wrapper = shallow(<RawOffers {...initialProps} />)
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

      describe('when keywords is not an empty string', () => {
        it('should update state with isLoading to true', () => {
          // when
          wrapper.instance().onSubmit(event)
          const expected = {
            hasMore: false,
            isLoading: true,
            keywordsValue: undefined,
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })

        it('should dispatch assignData with good params', () => {
          // when
          wrapper.instance().onSubmit(event)

          const expected = {
            patch: {
              offers: [],
            },
            type: 'ASSIGN_DATA',
          }

          // then
          expect(dispatchMock.mock.calls[0][0]).toEqual(expected)
          dispatchMock.mockClear()
        })

        it('should change query', () => {
          // when
          wrapper.instance().onSubmit(event)
          const expected = {
            keywords: 'AnyWord',
            page: null,
          }

          // then
          expect(queryChangeMock.mock.calls[0][0]).toEqual(expected)
          queryChangeMock.mockClear()
        })
      })

      describe('when keywords is an empty string', () => {
        it('should change query with mots-clés setted to null', () => {
          // given
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
          wrapper.instance().onSubmit(eventEmptyWord)
          const expected = {
            keywords: null,
            page: null,
          }

          // then
          expect(queryChangeMock.mock.calls[0][0]).toEqual(expected)
          queryChangeMock.mockClear()
        })
      })
    })
  })
})
