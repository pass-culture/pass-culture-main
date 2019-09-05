import { shallow } from 'enzyme'
import React from 'react'
import { Switch } from 'react-router-dom'

import Search from '../Search'
import Spinner from '../../../layout/Spinner'
import HeaderContainer from '../../../layout/Header/HeaderContainer'

const getPageContentDiv = wrapper => wrapper.find('.page-content')

const getPageContentForm = wrapper =>
  getPageContentDiv(wrapper)
    .props()
    .children.find(child => child.type === 'form')

const getPageContentFilter = wrapper =>
  getPageContentForm(wrapper).props.children.find(child => child.type.WrappedComponent)

const getPageContentSwitch = wrapper =>
  getPageContentDiv(wrapper)
    .props()
    .children.find(child => child.type === Switch)

const getPageContentSpinner = wrapper =>
  getPageContentSwitch(wrapper).props.children.find(child => child.type === Spinner)

const getSwitchedPageContent = path => wrapper => {
  const switchChildren = getPageContentSwitch(wrapper).props.children
  const pageContent =
    switchChildren.find(child => child && child.props.path === path) ||
    switchChildren
      .find(child => child && child.type === Switch)
      .props.children.find(child => child.props.path === path)
  return pageContent.props.render()
}

const getSearchResults = wrapper =>
  getSwitchedPageContent('/recherche/resultats/:menu(menu)?')(wrapper)

const getSearchSpinner = wrapper => getPageContentSpinner(wrapper)

const getSearchResultsFromCategory = wrapper =>
  getSwitchedPageContent('/recherche/resultats/:category([A-Z][a-z]+)/:menu(menu)?')(wrapper).props
    .children[1]

const getKeywordsInput = wrapper =>
  getPageContentForm(wrapper)
    .props.children[0].props.children.find(child => child.props.id === 'search-page-keywords-field')
    .props.children[0].props.children.find(child => child.props.id === 'keywords')

const getRefreshKeywordsButton = wrapper =>
  getPageContentForm(wrapper).props.children[0].props.children.find(
    child => child.props.id === 'search-page-keywords-field'
  ).props.children[0].props.children[2].props.children

const getFilterToggle = wrapper =>
  getPageContentForm(wrapper).props.children[0].props.children.find(
    child => child.props.id === 'search-filter-menu-toggle-button'
  ).props.children

describe('src | components | pages | Search', () => {
  // Initializing Mocks
  const dispatchMock = jest.fn()
  const queryChangeMock = jest.fn()
  const historyMock = { push: jest.fn() }

  describe('snapshot', () => {
    let props
    beforeEach(() => {
      props = {
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
            option: undefined,
          },
        },
        query: {
          change: queryChangeMock,
          parse: () => ({ page: '1' }),
        },
        recommendations: [],
        search: {},
        typeSublabels: [],
        typeSublabelsAndDescription: [],
      }
    })

    it('should match the snapshot', () => {
      // when
      const wrapper = shallow(<Search {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('switch Route', () => {
    describe('on the /recherche page', () => {
      let props
      beforeEach(() => {
        props = {
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
              option: undefined,
            },
          },
          query: {
            change: queryChangeMock,
            parse: () => ({ page: '1' }),
          },
          recommendations: [],

          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }
      })

      it('should render the page title', () => {
        // when
        const wrapper = shallow(<Search {...props} />)

        // then
        expect(wrapper.find(HeaderContainer).props().title).toBe('Recherche')
      })

      it('submitButton form is disabled', async () => {
        // given
        const wrapper = shallow(<Search {...props} />)

        // when
        const button = getPageContentForm(wrapper).props.children[0].props.children.find(
          child => child.props.id === 'search-page-keywords-field'
        ).props.children[1].props.children

        // then
        expect(button.props.disabled).toBe(true)
      })

      it('filter should be invisible', () => {
        // given
        const wrapper = shallow(<Search {...props} />)

        // when
        const searchFilterComponent = getPageContentFilter(wrapper)

        // then
        expect(searchFilterComponent.props.isVisible).toBe(false)
      })

      it('filter shoud be visible when state isFilterVisible is set to true ', () => {
        // given
        const wrapper = shallow(<Search {...props} />)

        // when
        const wrapperInstance = wrapper.instance()
        wrapperInstance.setState({ isFilterVisible: true })
        const searchFilterComponent = getPageContentFilter(wrapper)

        // then
        expect(searchFilterComponent.props.isVisible).toBe(true)
      })

      it('navByOfferType with path="/recherche"', () => {
        // given
        const wrapper = shallow(<Search {...props} />)

        // when
        const NavByOfferTypeComponent = getSwitchedPageContent('/recherche/:menu(menu)?')(wrapper)

        // then
        expect(NavByOfferTypeComponent.props.title).toBe('EXPLORER LES CATÉGORIES')
      })
    })

    describe('on /recherche/resultats page', () => {
      describe('on /recherche/resultats precisely', () => {
        let props
        beforeEach(() => {
          props = {
            dispatch: dispatchMock,
            history: historyMock,
            location: {
              hash: '',
              key: 'lxn6vp',
              pathname: '/recherche/resultats',
              search: '?orderBy=offer.id+desc',
              state: undefined,
            },
            match: {
              params: {
                results: 'resultats',
              },
            },
            query: {
              change: queryChangeMock,
              parse: () => ({ page: '1' }),
            },
            recommendations: [],

            search: {},
            typeSublabels: [],
            typeSublabelsAndDescription: [],
          }
        })

        it('should render the page title', () => {
          // given
          const wrapper = shallow(<Search {...props} />)

          // then
          expect(wrapper.find(HeaderContainer).props().title).toBe('Recherche : résultats')
        })

        it('searchResults with path="/recherche/resultats"', () => {
          // given
          const wrapper = shallow(<Search {...props} />)

          // when
          const SearchResults = getSearchResults(wrapper)

          // then
          expect(SearchResults.props.cameFromOfferTypesPage).toBe(false)
        })
      })

      describe('on /recherche/resultats/:category page', () => {
        let props
        beforeEach(() => {
          props = {
            dispatch: dispatchMock,
            history: historyMock,
            location: {
              hash: '',
              key: 'lxn6vp',
              pathname: '/recherche/resultats/Jouer',
              search: '?orderBy=offer.id+desc',
              state: undefined,
            },
            match: {
              params: {
                category: 'Jouer',
                results: 'resultats',
              },
            },
            query: {
              change: queryChangeMock,
              parse: () => ({
                categories: 'Jouer',
                'mots-cles': 'Fake',
              }),
            },
            recommendations: [],

            search: {},
            typeSublabels: [],
            typeSublabelsAndDescription: [
              {
                description:
                  'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?',
                sublabel: 'Jouer',
              },
            ],
          }
        })

        it('when search has finished loading should mount navResultsHeader & SearchResults with path="/recherche/resultats/:category"', () => {
          // given
          const wrapper = shallow(<Search {...props} />)
          wrapper.setState({ isLoading: false })

          // when
          const ResultsRoute = getSwitchedPageContent(
            '/recherche/resultats/:category([A-Z][a-z]+)/:menu(menu)?'
          )(wrapper)
          const NavResultsHeader = ResultsRoute.props.children[0]
          const SearchResults = getSearchResultsFromCategory(wrapper)

          // then
          expect(NavResultsHeader.props.category).toBe('Jouer')
          expect(NavResultsHeader.props.description).toBe(
            'Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?'
          )
          expect(SearchResults.props.keywords).toBe('Fake')
          expect(SearchResults.props.cameFromOfferTypesPage).toBe(true)
        })

        it('should mount loading spinner when search is loading', () => {
          // given
          const wrapper = shallow(<Search {...props} />)
          wrapper.setState({ isLoading: true })

          // when
          const Spinner = getSearchSpinner(wrapper)

          // then
          expect(Spinner.key).toBe('loader')
          expect(Spinner.props.label).toBe('Recherche en cours')
        })
      })
    })
  })

  describe('functions', () => {
    describe('constructor', () => {
      let props
      beforeEach(() => {
        props = {
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
              option: undefined,
            },
          },
          query: {
            change: queryChangeMock,
            parse: () => ({ page: '1' }),
          },
          recommendations: [],

          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }
      })

      it('should initialize state correctly', () => {
        // given
        props.query.parse = () => ({ 'mots-cles': 'Fake' })

        // when
        const wrapper = shallow(<Search {...props} />)
        const expected = {
          isLoading: false,
          hasMore: false,
          isFilterVisible: false,
          keywordsKey: 0,
          keywordsValue: 'Fake',
        }

        // then
        expect(wrapper.state()).toStrictEqual(expected)
      })
    })

    describe('handleDataRequest', () => {
      describe('on resultats page', () => {
        let props
        beforeEach(() => {
          props = {
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
                option: undefined,
              },
            },
            query: {
              change: queryChangeMock,
              parse: () => ({ page: '1' }),
            },
            recommendations: [],

            search: {},
            typeSublabels: [],
            typeSublabelsAndDescription: [],
          }
        })

        it('should dispatch requestDataTypes when component is rendered', () => {
          // when
          const wrapper = shallow(<Search {...props} />)
          wrapper.instance().componentDidMount()
          const expectedRequestedGetTypes = {
            config: {
              apiPath: '/types',
              method: 'GET',
            },
            type: 'REQUEST_DATA_GET_/TYPES',
          }

          // then
          expect(dispatchMock.mock.calls[1][0]).toStrictEqual(expectedRequestedGetTypes)
        })
      })
    })

    describe('back link', () => {
      describe('on results page', () => {
        describe('getBackToUrl()', () => {
          let props
          beforeEach(() => {
            props = {
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
                  results: 'resultats',
                },
              },
              query: {
                change: queryChangeMock,
                parse: () => ({ page: '1' }),
              },
              recommendations: [],

              search: {},
              typeSublabels: [],
              typeSublabelsAndDescription: [],
            }
          })

          it('should back to /recherche', () => {
            // given
            const wrapper = shallow(<Search {...props} />)

            // when
            const url = wrapper.instance().getBackToUrl()

            // then
            expect(url).toBe('/recherche')
          })
        })

        describe('reinitializeStates()', () => {
          let props
          beforeEach(() => {
            props = {
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
                  option: undefined,
                },
              },
              query: {
                change: queryChangeMock,
                parse: () => ({ page: '1' }),
              },
              recommendations: [],

              search: {},
              typeSublabels: [],
              typeSublabelsAndDescription: [],
            }
          })

          it('should reinitialize states when click the back link', () => {
            // given
            const wrapper = shallow(<Search {...props} />)

            // when
            wrapper.instance().reinitializeStates()

            // then
            expect(wrapper.state()).toStrictEqual({
              isLoading: false,
              hasMore: false,
              isFilterVisible: false,
              keywordsKey: 1,
              keywordsValue: '',
            })
          })
        })
      })

      describe('not on results page', () => {
        let props
        beforeEach(() => {
          props = {
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
                option: undefined,
              },
            },
            query: {
              change: queryChangeMock,
              parse: () => ({ page: '1' }),
            },
            recommendations: [],

            search: {},
            typeSublabels: [],
            typeSublabelsAndDescription: [],
          }
        })

        it('should not display back button', () => {
          // when
          const wrapper = shallow(<Search {...props} />)

          // then
          expect(wrapper.contains('.back-link')).toBe(false)
        })
      })
    })

    describe('handleOnSubmit', () => {
      // when
      const props = {
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
            option: undefined,
          },
        },
        query: {
          change: queryChangeMock,
          parse: () => ({ page: '1' }),
        },
        recommendations: [],
        search: {},
        typeSublabels: [],
        typeSublabelsAndDescription: [],
      }
      const wrapper = shallow(<Search {...props} />)
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

      describe('when keywords is not an empty string', () => {
        it('should update state with mots-clés set to value given', () => {
          // when
          wrapperInstance.handleOnSubmit(event)

          const expected = {
            isLoading: false,
            hasMore: false,
            isFilterVisible: false,
            keywordsKey: 0,
            keywordsValue: undefined,
          }

          // then
          expect(wrapper.state()).toStrictEqual(expected)
        })

        it('should change query', () => {
          // when
          wrapperInstance.handleOnSubmit(event)

          const argument1 = {
            'mots-cles': 'AnyWord',
            page: 1,
          }
          const argument2 = {
            pathname: '/recherche/resultats/tout',
          }

          // then
          expect(queryChangeMock).toHaveBeenCalledWith(argument1, argument2)
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
                keywords: {
                  value: '',
                },
              },
            },
          })

          // when
          wrapperInstance.handleOnSubmit(eventEmptyWord)

          // then
          const argument1 = {
            'mots-cles': null,
            page: 1,
          }
          const argument2 = {
            pathname: '/recherche/resultats/tout',
          }

          // then
          expect(queryChangeMock).toHaveBeenCalledWith(argument1, argument2)
          queryChangeMock.mockClear()
        })
      })
    })

    describe('onKeywoFilterByDates.spec.jsrdsEraseClick', () => {
      let props
      beforeEach(() => {
        props = {
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
              option: undefined,
            },
          },
          query: {
            change: queryChangeMock,
            parse: () => ({ page: '1' }),
          },
          recommendations: [],

          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }
      })

      it('button should not appear when no char has been typed', () => {
        // when
        const wrapper = shallow(<Search {...props} />)
        const button = wrapper.find('form').find('#refresh-keywords-button')

        // then
        expect(button).not.toHaveProperty('onClick')
      })

      it('should update state when one char has been typed', () => {
        // given
        const wrapper = shallow(<Search {...props} />)
        const wrapperInstance = wrapper.instance()
        wrapperInstance.setState({ keywordsValue: 'A' })

        // when
        const button = getRefreshKeywordsButton(wrapper)
        button.props.onClick()

        const expected = {
          isLoading: false,
          hasMore: false,
          isFilterVisible: false,
          keywordsKey: 1,
          keywordsValue: '',
        }

        // then
        expect(wrapper.state()).toStrictEqual(expected)
      })

      it('should change navigation', () => {
        // given
        const wrapper = shallow(<Search {...props} />)
        const wrapperInstance = wrapper.instance()
        wrapperInstance.setState({ keywordsValue: 'A' })

        // when
        wrapperInstance.setState({ keywordsValue: 'A' })
        const button = getRefreshKeywordsButton(wrapper)
        button.props.onClick()

        // then
        expect(wrapperInstance.state.keywordsValue).toBe('')
        queryChangeMock.mockClear()
      })
    })

    describe('onKeywordsChange', () => {
      // when
      // when
      const props = {
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
            option: undefined,
          },
        },
        query: {
          change: queryChangeMock,
          parse: () => ({ page: '1' }),
        },
        recommendations: [],
        search: {},
        typeSublabels: [],
        typeSublabelsAndDescription: [],
      }
      const wrapper = shallow(<Search {...props} />)
      const event = {
        target: {
          value: 'Any',
        },
      }

      const wrapperInstance = wrapper.instance()
      wrapperInstance.setState({ isFilterVisible: true })

      it('should update state with keywords value', () => {
        // when
        getKeywordsInput(wrapper).props.onChange(event)

        // then
        const expected = {
          isLoading: false,
          hasMore: false,
          isFilterVisible: true,
          keywordsKey: 0,
          keywordsValue: 'Any',
        }

        // then
        expect(wrapper.state()).toStrictEqual(expected)
      })
    })

    describe('onClickOpenCloseFilterDiv', () => {
      describe('when user does not click on the icon button', () => {
        // given
        const props = {
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
              option: undefined,
            },
          },
          query: {
            change: queryChangeMock,
            parse: () => ({ page: '1' }),
          },
          recommendations: [],

          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }
        const wrapper = shallow(<Search {...props} />)

        // when
        const filterToggleIcon = getFilterToggle(wrapper).props.children

        it('should show ico-filter', () => {
          // then
          expect(filterToggleIcon.props.svg).toBe('ico-filter')
        })

        it('isFilterVisible state is false', () => {
          const expected = {
            isLoading: false,
            hasMore: false,
            isFilterVisible: false,
            keywordsKey: 0,
            keywordsValue: undefined,
          }

          // then
          expect(filterToggleIcon.props.svg).toBe('ico-filter')
          expect(wrapper.state()).toStrictEqual(expected)
        })
      })

      describe('when user click on the icon button', () => {
        // when
        // when
        const props = {
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
              option: undefined,
            },
          },
          query: {
            change: queryChangeMock,
            parse: () => ({ page: '1' }),
          },
          recommendations: [],

          search: {},
          typeSublabels: [],
          typeSublabelsAndDescription: [],
        }
        const wrapper = shallow(<Search {...props} />)
        const filterToggle = getFilterToggle(wrapper)
        filterToggle.props.onClick(true)
        const filterToggleIcon = getFilterToggle(wrapper).props.children

        it('should update isFilterVisible state to true', () => {
          const expected = {
            isLoading: false,
            hasMore: false,
            isFilterVisible: true,
            keywordsKey: 0,
            keywordsValue: undefined,
          }

          // then
          expect(wrapper.state()).toStrictEqual(expected)
        })

        it('should show chevron-up icon', () => {
          expect(filterToggleIcon.props.svg).toBe('ico-chevron-up')
        })
      })

      describe('when there is some filters in search', () => {
        it('should show ico-filter-active icon', () => {
          // given
          const props = {
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
                option: undefined,
              },
            },
            query: {
              change: queryChangeMock,
              parse: () => ({
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
              }),
            },
            recommendations: [],

            search: {},
            typeSublabels: [],
            typeSublabelsAndDescription: [],
          }

          // when
          const wrapper = shallow(<Search {...props} />)
          const filterToggleIcon = getFilterToggle(wrapper).props.children

          // then
          expect(filterToggleIcon.props.svg).toBe('ico-filter-active')
        })
      })
    })
  })
})
