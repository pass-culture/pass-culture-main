import React from 'react'
import { shallow } from 'enzyme'

import SearchPageContent from '../SearchPageContent'

describe('src | components | pages | SearchPageContentContent', () => {
  // Initializing Mocks
  const dispatchMock = jest.fn()
  const paginationChangeMock = jest.fn()
  const goToNextPageMock = jest.fn()
  const historyMock = { push: jest.fn() }

  const initialProps = {
    dispatch: dispatchMock,
    history: historyMock,
    location: {
      hash: '',
      key: 'lxn6vp',
      pathname: '/recherche',
      search: '?orderBy=offer.id+desc',
      state: undefined,
    },
    match: {
      params: {
        categorie: undefined,
        view: undefined,
      },
    },
    pagination: {
      apiQueryString: 'orderBy=offer.id+desc',
      change: paginationChangeMock,
      goToNextPage: goToNextPageMock,
      page: 1,
      windowQuery: {
        categories: null,
        date: null,
        distance: null,
        jours: null,
        latitude: null,
        longitude: null,
        'mots-cles': null,
        orderBy: 'offer.id+desc',
      },
    },
    recommendations: [],
    search: {},
    typeSublabels: [],
    typeSublabelsAndDescription: [],
  }

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    describe('Main', () => {
      describe('Home', () => {
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const button = wrapper.find('button').at(0)
        it('should render the page title', () => {
          expect(wrapper.props().pageTitle).toEqual('Recherche')
        })
        it('contains a closeSearchButton', () => {
          expect(wrapper.props().closeSearchButton).toEqual(true)
        })
        it('submitButton form is disabled', () => {
          expect(button.props().disabled).toEqual(true)
        })
      })
    })
    describe('SearchFilter', () => {
      describe('When arriving on page search', () => {
        it('should be invisible', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          const searchFilterComponent = wrapper.find('SearchFilter')

          // then
          expect(searchFilterComponent.props().isVisible).toEqual(false)
        })
      })
      describe('when state isFilterVisible is setted to true ', () => {
        it('should be visible', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          const wrapperInstance = wrapper.instance()
          wrapperInstance.setState({ isFilterVisible: true })

          const searchFilterComponent = wrapper.find('SearchFilter')

          // then
          expect(searchFilterComponent.props().isVisible).toEqual(true)
        })
      })

      // Close button // wrapper.props().closeSearchButton
      // console.log('|||||| Wrapper Props', wrapper.props().backButton);
      // pageTitle={searchPageTitle}
    })
  })

  describe('Switch Route', () => {
    it('NavByOfferType with path="/recherche"', () => {
      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const switchRouteComponent = wrapper.find('Route')
      const NavByOfferTypeComponent = switchRouteComponent
        .at(0)
        .props()
        .render()

      // then
      expect(NavByOfferTypeComponent.props.title).toEqual('PAR CATÉGORIES')
    })
    it('NavResultsHeader & SearchResults with path="/recherche/resultats/:categorie"', () => {
      // given
      initialProps.location.pathname = '/recherche/resultats/'
      initialProps.pagination.windowQueryString =
        'categories=Jouer&orderBy=offer.id+desc'
      initialProps.pagination.windowQuery.categories = 'Jouer'
      initialProps.pagination.windowQuery['mots-cles'] = 'Fake'
      initialProps.typeSublabelsAndDescription = [
        {
          description:
            'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
          sublabel: 'Jouer',
        },
      ]

      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const switchRouteComponent = wrapper.find('Route')
      const NavResultsHeaderComponent = switchRouteComponent
        .at(1)
        .props()
        .render()[0]
      const SearchResultsComponent = switchRouteComponent
        .at(1)
        .props()
        .render()[1]

      // then
      expect(NavResultsHeaderComponent.props.category).toEqual('Jouer')
      expect(NavResultsHeaderComponent.props.description).toEqual(
        'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?'
      )
      expect(SearchResultsComponent.props.keywords).toEqual('Fake')
      expect(SearchResultsComponent.props.withNavigation).toEqual(true)
    })
    it('SearchResults with path="/recherche/resultats"', () => {
      // given
      initialProps.pagination.windowQueryString =
        'categories=Jouer&orderBy=offer.id+desc'

      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const switchRouteComponent = wrapper.find('Route')
      const SearchResultsComponent = switchRouteComponent
        .at(2)
        .props()
        .render()

      // then
      expect(SearchResultsComponent.props.pagination.windowQueryString).toEqual(
        'categories=Jouer&orderBy=offer.id+desc'
      )
      expect(SearchResultsComponent.props.withNavigation).toEqual(false)
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        initialProps.pagination.windowQuery['mots-cles'] = 'Fake'
        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const expected = {
          isFilterVisible: false,
          keywordsKey: 0,
          keywordsValue: 'Fake',
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })

    describe('handleDataRequest', () => {
      describe('When arriving for the first time on search page with page = 1', () => {
        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        wrapper.instance().handleDataRequest()

        it('should first dispatch requestDataTypes when component is rendered', () => {
          const expectedRequestedGetTypes = {
            config: {},
            method: 'GET',
            path: 'types',
            type: 'REQUEST_DATA_GET_TYPES',
          }

          // THEN
          expect(dispatchMock.mock.calls.length).toBe(2)
          expect(dispatchMock.mock.calls[0][0]).toEqual(
            expectedRequestedGetTypes
          )
        })

        it('should in a second time, dispatch requestData for recommendations based on apiQueryString when component is rendered', () => {
          const expectedRequestData = {
            config: {
              handleFail: () => {},
              handleSuccess: () => {},
            },
            method: 'GET',
            path: 'recommendations?page=1&orderBy=offer.id+desc',
            type: 'REQUEST_DATA_GET_RECOMMENDATIONS?PAGE=UNDEFINED&UNDEFINED',
          }

          // then
          expect(dispatchMock.mock.calls.length).toBe(2)
          expect(dispatchMock.mock.calls[1][0].path).toEqual(
            expectedRequestData.path
          )
        })
      })

      describe.skip('when ??? page !== 1 && search.page && page === Number(search.page) ', () => {
        // TODO

        it('should ???', () => {
          // given
          dispatchMock.mockClear()
          initialProps.pagination.page = 2

          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          wrapper.instance().handleDataRequest()

          // expect
          expect(dispatchMock.mock.calls.length).toBe(2)
        })
      })

      describe.skip('goToNextPage', () => {})
    })

    describe('loadMoreHandler', () => {
      // given
      xit('should call handleDataRequest to request more offers', () => {
        // const handleDataRequestInstanceFc = wrapper.instance().handleDataRequest()
        // jest.mock(handleDataRequestInstanceFc)
        // const spy = jest.spyOn(wrapper.instance(), 'handleDataRequest')
        // when
      })
      xit('should change history location', () => {
        // given
        initialProps.pagination.windowQueryString =
          'categories=Jouer&orderBy=offer.id+desc'

        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        wrapper.instance().loadMoreHandler()
        const expected =
          '/recherche?page=1&categories=Jouer&orderBy=offer.id+desc'

        // then
        expect(historyMock.push).toHaveBeenCalledWith(expected)
      })
    })

    describe('onBackToSearchHome', () => {
      describe('On results page', () => {
        // Given
        initialProps.match.params.view = 'resultats'

        it('should update state', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          wrapper.props().backButton.onClick()

          const expected = {
            isFilterVisible: false,
            keywordsKey: 1,
            keywordsValue: '',
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should change pagination', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          wrapper.props().backButton.onClick()

          const argument1 = {
            categories: null,
            date: null,
            jours: null,
            'mots-cles': null,
          }
          const argument2 = { pathname: '/recherche' }

          // then
          expect(paginationChangeMock).toHaveBeenCalledWith(
            argument1,
            argument2
          )
          paginationChangeMock.mockClear()
        })
      })
      describe('Not on results page', () => {
        it('should not display back button', () => {
          // given
          initialProps.match.params.view = ''

          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)

          // then
          expect(wrapper.props().backButton).toEqual(false)
        })
      })
    })

    describe('onSubmit', () => {
      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const event = Object.assign(jest.fn(), {
        preventDefault: () => {},
        target: {
          elements: {
            keywords: {
              value: 'AnyWord',
            },
          },
        },
      })
      const wrapperInstance = wrapper.instance()
      wrapperInstance.setState({ isFilterVisible: true })
      describe('when keywords is an empty string', () => {
        it('should update state with mots-clés setted to value given', () => {
          // when
          wrapper.find('form').simulate('submit', event)

          const expected = {
            isFilterVisible: false,
            keywordsKey: 0,
            keywordsValue: null,
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should change pagination', () => {
          // when
          wrapper.find('form').simulate('submit', event)

          const argument1 = {
            'mots-cles': 'AnyWord',
          }
          const argument2 = {
            isClearingData: true,
            pathname: '/recherche/resultats',
          }

          // then
          expect(paginationChangeMock).toHaveBeenCalledWith(
            argument1,
            argument2
          )
          paginationChangeMock.mockClear()
        })
      })

      describe('when keywords is an empty string', () => {
        it('should change pagination with mots-clés setted to null', () => {
          // given
          const eventEmptyWord = Object.assign(jest.fn(), {
            preventDefault: () => {},
            target: {
              elements: {
                keywords: {
                  value: '',
                },
              },
            },
          })

          // when
          wrapper.find('form').simulate('submit', eventEmptyWord)

          // then
          const argument1 = {
            'mots-cles': null,
          }
          const argument2 = {
            isClearingData: false,
            pathname: '/recherche/resultats',
          }

          // then
          expect(paginationChangeMock).toHaveBeenCalledWith(
            argument1,
            argument2
          )
          paginationChangeMock.mockClear()
        })
      })
    })

    describe('onKeywoFilterByDates.spec.jsrdsEraseClick', () => {
      describe('when no char has been typed', () => {
        it('button should not appear', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          const button = wrapper.find('form').find('#refresh-keywords-button')

          // then
          expect(button).not.toHaveProperty('onClick')
        })
      })

      describe('when one char has been typed', () => {
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const wrapperInstance = wrapper.instance()
        wrapperInstance.setState({ keywordsValue: 'A' })

        it('should update state', () => {
          // when
          const button = wrapper.find('form').find('#refresh-keywords-button')
          button.props().onClick()

          const expected = {
            isFilterVisible: false,
            keywordsKey: 1,
            keywordsValue: '',
          }
          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should change navigation', () => {
          wrapperInstance.setState({ keywordsValue: 'A' })
          const button = wrapper.find('form').find('#refresh-keywords-button')
          button.props().onClick()

          // then
          expect(paginationChangeMock).toHaveBeenCalled()
          paginationChangeMock.mockClear()
        })
      })
    })

    describe('onKeywordsChange', () => {
      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const event = {
        target: {
          value: 'Any',
        },
      }

      const wrapperInstance = wrapper.instance()
      wrapperInstance.setState({ isFilterVisible: true })

      it('should update state with keywords value', () => {
        // when
        wrapper.find('#keywords').simulate('change', event)

        // then
        const expected = {
          isFilterVisible: true,
          keywordsKey: 0,
          keywordsValue: 'Any',
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })

    describe('onClickOpenCloseFilterDiv', () => {
      describe('When user does not click on the icon button', () => {
        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const toogleIcon = wrapper
          .find('#search-filter-menu-toggle-button')
          .find('Icon')

        it('should show ico-filter', () => {
          expect(toogleIcon.props('svg')).toEqual({ svg: 'ico-filter' })
        })
        it('isFilterVisible state is false', () => {
          const expected = {
            isFilterVisible: false,
            keywordsKey: 0,
            keywordsValue: null,
          }

          // then
          expect(toogleIcon.props('svg')).toEqual({ svg: 'ico-filter' })
          expect(wrapper.state()).toEqual(expected)
        })
      })

      describe('When user click on the icon button', () => {
        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const toogleIcon = wrapper
          .find('#search-filter-menu-toggle-button')
          .find('button')
        toogleIcon.simulate('click', false)

        it('should update isFilterVisible state to true', () => {
          const expected = {
            isFilterVisible: true,
            keywordsKey: 0,
            keywordsValue: null,
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should show chevron-up icon', () => {
          const toogleIconClicked = wrapper
            .find('#search-filter-menu-toggle-button')
            .find('button')

          expect(toogleIconClicked.find('Icon').props('svg')).toEqual({
            svg: 'ico-chevron-up',
          })
        })
      })

      describe('When there is some filters in search', () => {
        it('should show ico-filter-active icone', () => {
          // given
          initialProps.pagination.windowQuery = {
            categories: '%C3%89couter,Pratiquer',
            date: '2018-09-25T09:38:20.576Z',
            days: null,
            distance: null,
            jours: '0-1,1-5,5-100000',
            latitude: null,
            longitude: null,
            [`mots-cles`]: null,
            page: '2',
            types: null,
          }

          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          const toogleIcon = wrapper
            .find('#search-filter-menu-toggle-button')
            .find('button')

          // then
          expect(toogleIcon.find('Icon').props('svg')).toEqual({
            svg: 'ico-filter-active',
          })
        })
      })
    })
  })
})
