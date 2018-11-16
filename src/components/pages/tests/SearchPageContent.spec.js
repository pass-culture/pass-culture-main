import React from 'react'
import { shallow } from 'enzyme'
import { Icon } from 'pass-culture-shared'

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

  describe('functions', () => {
    describe('constructor', () => {
      it('should initialize state correctly', () => {
        // given
        initialProps.pagination.windowQuery['mots-cles'] = 'Fake'
        // when
        const wrapper = shallow(<SearchPageContent {...initialProps} />)
        const expected = {
          keywordsKey: 0,
          keywordsValue: 'Fake',
          withFilter: false,
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
      it('should change history location', () => {
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
      const pathname = '/recherche'
      const { pagination } = initialProps
      let keywordsKey

      describe('Visible on results page', () => {
        // Given
        initialProps.match.params.view = 'resultats'

        it('should update state', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          keywordsKey = 4
          wrapper
            .instance()
            .onBackToSearchHome(pathname, pagination, keywordsKey)

          // le backButton est dans Main qui est connecté et contient des hocs -> très compliqué d'y accéder via le shallow
          // wrapper.find('Main').find('backButton').simulate('onClick')

          const expected = {
            keywordsKey: 5,
            keywordsValue: '',
            withFilter: false,
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should change pagination', () => {
          // when
          const wrapper = shallow(<SearchPageContent {...initialProps} />)
          keywordsKey = { ...wrapper.state() }
          wrapper
            .instance()
            .onBackToSearchHome(pathname, pagination, keywordsKey)
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
        describe.skip('Invisible on results page', () => {
          it('should not display back button', () => {
            // TO DO
          })
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
      wrapperInstance.setState({ withFilter: true })
      describe('when keywords is an empty string', () => {
        it('should update state', () => {
          // when
          wrapper.find('form').simulate('submit', event)

          // then
          const expected = {
            keywordsKey: 0,
            keywordsValue: null,
            withFilter: false,
          }

          // then
          expect(wrapper.state()).toEqual(expected)
        })
        it('should change pagination', () => {
          // when
          wrapper.find('form').simulate('submit', event)

          // then
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
        it('should change pagination', () => {
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

    describe.skip('onClickOpenCloseFilterDiv', () => {
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const toogleIcon = wrapper
        .find('#search-filter-menu-toggle-button')
        .find(Icon)

      describe('when filter is not open', () => {
        it('should update withFilter value to true', () => {
          // when
          wrapper
            .find('#search-filter-menu-toggle-button')
            .find('button')
            .simulate('onClick')

          // wrapper.instance().onClickOpenCloseFilterDiv(wrapper.state().withFilter)

          // then
          expect(toogleIcon.props('svg')).toEqual({ svg: 'ico-chevron-up' })
          // expect(wrapper.state()).toEqual(expected)
        })
      })
      describe('when filter is already open', () => {
        it('should update withFilter value to false ', () => {
          // when
          const wrapperInstance = wrapper.instance()
          wrapperInstance.setState({ withFilter: true })

          wrapper
            .find('#search-filter-menu-toggle-button')
            .find('button')
            .simulate('onClick')
          // const expected = {
          //   withFilter: false
          // }
          // then

          expect(toogleIcon.props('svg')).toEqual({ svg: 'ico-filter' })
          // expect(wrapper.state()).toEqual(expected)
        })
      })
    })

    describe.skip('onKeywordsChange', () => {
      // when
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const event = Object.assign(jest.fn(), {
        preventDefault: () => {},
        target: {
          elements: {
            keywords: {
              value: 'Any',
            },
          },
        },
      })
      const wrapperInstance = wrapper.instance()
      wrapperInstance.setState({ withFilter: true })

      it('should update state', () => {
        // when
        wrapper.find('input').simulate('change', event)

        // then
        const expected = {
          keywordsKey: 0,
          keywordsValue: 'Any',
          withFilter: true,
        }

        // then
        expect(wrapper.state()).toEqual(expected)
      })
    })

    describe.only('onKeywordsEraseClick', () => {
      // GIven
      initialProps.pagination.windowQuery[`mots-cles`] = 'A'
      const { pathname } = initialProps.location
      const wrapper = shallow(<SearchPageContent {...initialProps} />)
      const wrapperInstance = wrapper.instance()
      const wrapperState = wrapper.state()

      describe('when no char has been typed', () => {
        it('button should not appear', () => {
          const button = wrapper.find('form').find('#refresh-keywords-button')
          console.log('>>>>>>>>>>>>>>> button >>>>> ', button)

          expect(button).toHaveLength(0)
          expect(button.exists()).toEqual(false)
        })
      })
      describe('when one char has been typed', () => {
        wrapperInstance.setState({ keywordsValue: 'A' })
        console.log(' /////// wrapper state >>>>>>>>>>>> ', wrapperState)

        // const { keywordsKey } =  wrapperState
        it('should update state', () => {
          // when
          wrapper.instance().onKeywordsEraseClick()
          const expected = {
            keywordsKey: 1,
            keywordsValue: '',
            withFilter: false,
          }
          // then
          expect(wrapperState).toEqual(expected)
        })
        it('should change navigation', () => {
          console.log('wrapperState navigation ---- ', wrapperState)
          wrapper.instance().onKeywordsEraseClick('llulu', 'lala', 'toyoy')
          const argument1 = { 'mots-cles': null }
          const argument2 = { pathname }

          // then
          expect(paginationChangeMock).toHaveBeenCalledWith(
            argument1,
            argument2
          )
          paginationChangeMock.mockClear()
        })
      })
    })
  })

  // Bouton recherchre avec props disabled si !isOneCharInKeywords

  // describe('render', () => {
  //   describe('SearchFilter', () => {
  //     it('should be visible', () => {
  //
  //     })
  //   })
  // })
})

// Titre de la page selon s'il y a des recommendations ou pas.
