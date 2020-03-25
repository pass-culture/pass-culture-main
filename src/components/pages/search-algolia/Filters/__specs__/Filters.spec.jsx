import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'
import { fetchAlgolia } from '../../../../../vendor/algolia/algolia'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import { Criteria } from '../../Criteria/Criteria'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import FilterCheckbox from '../FilterCheckbox/FilterCheckbox'
import { Filters } from '../Filters'

jest.mock('../../../../../vendor/algolia/algolia', () => ({
  fetchAlgolia: jest.fn(),
}))
describe('components | Filters', () => {
  let props

  beforeEach(() => {
    props = {
      geolocation: {
        latitude: 40,
        longitude: 41,
      },
      history: {
        location: {
          pathname: '',
          search: '',
        },
        listen: jest.fn(),
        push: jest.fn(),
        replace: jest.fn(),
      },
      initialFilters: {
        offerCategories: ['VISITE', 'CINEMA'],
        isSearchAroundMe: false,
        offerTypes: {
          isDigital: false,
          isEvent: false,
          isThing: false
        },
        sortCriteria: '_by_price',
      },
      isGeolocationEnabled: false,
      isUserAllowedToSelectCriterion: jest.fn(),
      match: {
        params: {},
      },
      offers: {
        hits: [],
        nbHits: 0,
        nbPages: 0,
      },
      query: {
        parse: jest.fn(),
      },
      redirectToSearchFiltersPage: jest.fn(),
      showFailModal: jest.fn(),
      updateFilteredOffers: jest.fn(),
      updateFilters: jest.fn(),
    }
  })

  describe('render', () => {
    describe('localisation filter page', () => {
      it('should render localisation filter page when on route /recherche-offres/filtres/localisation', () => {
        // given
        props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(Criteria)
        expect(criteria).toHaveLength(1)
        expect(criteria.prop('backTo')).toStrictEqual(
          '/recherche-offres/resultats/filtres?mots-cles=librairie'
        )
        expect(criteria.prop('criteria')).toStrictEqual(GEOLOCATION_CRITERIA)
        expect(criteria.prop('history')).toStrictEqual(props.history)
        expect(criteria.prop('match')).toStrictEqual(props.match)
        expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
        expect(criteria.prop('title')).toStrictEqual('Localisation')
      })

      it('should render a Criteria component with a "Partout" criterion when not searching around me', () => {
        // given
        props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
        props.initialFilters.isSearchAroundMe = false

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const criteria = wrapper.find(Criteria)
        expect(criteria.prop('activeCriterionLabel')).toStrictEqual('Partout')
      })

      describe('when searching everywhere', () => {
        it('should trigger search to Algolia and redirect to filters page when clicking on "Partout" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
          })
          props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
          props.isUserAllowedToSelectCriterion.mockReturnValue(true)
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'non',
            categories: 'VISITE;CINEMA',
            'mots-cles': 'librairie',
            tri: '_by_price',
          })
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )
          const wrapper = mount(
            <Router history={props.history}>
              <Filters {...props} />
            </Router>
          )
          const everywhereButton = wrapper
            .find(Criteria)
            .find('button')
            .first()

          // when
          everywhereButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            categories: ['VISITE', 'CINEMA'],
            geolocationCoordinates: null,
            indexSuffix: '_by_price',
            keywords: 'librairie',
            offerTypes: {
              isDigital: false,
              isEvent: false,
              isThing: false
            },
            page: 0,
          })
          expect(props.redirectToSearchFiltersPage).toHaveBeenCalledWith()
          expect(props.history.replace).toHaveBeenCalledWith({
            search: '?mots-cles=librairie&autour-de-moi=non&tri=_by_price&categories=VISITE;CINEMA',
          })
        })
      })

      describe('when searching around me', () => {
        it('should trigger search to Algolia and redirect to filters page when clicking on "Autour de moi" criterion', () => {
          // given
          props.history = createBrowserHistory()
          jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
          })
          props.history.location.pathname = '/recherche-offres/resultats/filtres/localisation'
          props.initialFilters = {
            offerCategories: ['VISITE'],
            isSearchAroundMe: false,
            offerTypes: { isDigital: false },
            sortCriteria: '_by_price',
          }
          props.isUserAllowedToSelectCriterion.mockReturnValue(true)
          props.query.parse.mockReturnValue({
            'autour-de-moi': 'oui',
            categories: 'VISITE',
            'mots-cles': 'librairie',
            tri: '_by_price',
          })
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )
          const wrapper = mount(
            <Router history={props.history}>
              <Filters {...props} />
            </Router>
          )
          const aroundMeButton = wrapper
            .find(Criteria)
            .find('button')
            .at(1)

          // when
          aroundMeButton.simulate('click')

          // then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            categories: ['VISITE'],
            geolocationCoordinates: { latitude: 40, longitude: 41 },
            indexSuffix: '_by_price',
            keywords: 'librairie',
            offerTypes: { isDigital: false },
            page: 0,
          })
          expect(props.redirectToSearchFiltersPage).toHaveBeenCalledWith()
          expect(props.history.replace).toHaveBeenCalledWith({
            search: '?mots-cles=librairie&autour-de-moi=oui&tri=_by_price&categories=VISITE',
          })
        })
      })
    })

    describe('filters page', () => {
      it('should render a Header component with the right props', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.history.location.search = '?mots-cles=librairie'

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const header = wrapper.find(HeaderContainer)
        expect(header).toHaveLength(1)
        expect(header.prop('backTo')).toStrictEqual(
          '/recherche-offres/resultats?mots-cles=librairie'
        )
        expect(header.prop('closeTo')).toBeNull()
        expect(header.prop('reset')).toStrictEqual(expect.any(Function))
        expect(header.prop('title')).toStrictEqual('Filtrer')
      })

      it('should display the number of results on the display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 10

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper
          .findWhere(node => node.text() === 'Afficher les 10 résultats')
          .first()
        expect(numberOfResults).toHaveLength(1)
      })

      it('should display "999+" on the display results button when number of results exceeds 999', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 1000

        // when
        const wrapper = shallow(<Filters {...props} />)

        // then
        const numberOfResults = wrapper
          .findWhere(node => node.text() === 'Afficher les 999+ résultats')
          .first()
        expect(numberOfResults).toHaveLength(1)
      })

      it('should filter offers when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.offers.nbHits = 1000
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilteredOffers).toHaveBeenCalledWith({
          hits: [],
          nbHits: 1000,
          nbPages: 0,
        })
      })

      it('should redirect to results page with query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        props.history.location.search = '?mots-cles=librairie'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith(
          '/recherche-offres/resultats?mots-cles=librairie'
        )
      })

      it('should redirect to results page with no query param when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.history.push).toHaveBeenCalledWith('/recherche-offres/resultats')
      })

      it('should update filters when clicking on display results button', () => {
        // given
        props.history.location.pathname = '/recherche-offres/filtres'
        const wrapper = shallow(<Filters {...props} />)
        const resultsButton = wrapper.find('.sf-button')

        // when
        resultsButton.simulate('click')

        // then
        expect(props.updateFilters).toHaveBeenCalledWith({
          offerCategories: ['VISITE', 'CINEMA'],
          isSearchAroundMe: false,
          offerTypes: {
            isDigital: false,
            isEvent: false,
            isThing: false
          },
          sortCriteria: '_by_price'
        })
      })

      describe('geolocation filter', () => {
        it('should display a "Localisation" title for geolocation filter', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.findWhere(node => node.text() === 'Localisation').first()
          expect(title).toHaveLength(1)
        })

        it('should display a "Partout" for geolocation filter when initial filter is "Partout"', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = false

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.findWhere(node => node.text() === 'Partout').first()
          expect(button).toHaveLength(1)
        })

        it('should display a "Autour de moi" for geolocation filter when initial filter is "Autour de moi"', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = true

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()
          expect(button).toHaveLength(1)
        })

        it('should redirect to localisation filter page with given query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.history.location.search = '?mots-cles=librairie'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche-offres/resultats/filtres/localisation?mots-cles=librairie'
          )
        })

        it('should redirect to localisation filter page with no query params when clicking on geolocation filter button', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.isSearchAroundMe = true
          const wrapper = shallow(<Filters {...props} />)
          const button = wrapper.findWhere(node => node.text() === 'Autour de moi').first()

          // when
          button.simulate('click')

          // then
          expect(props.history.push).toHaveBeenCalledWith(
            '/recherche-offres/resultats/filtres/localisation'
          )
        })
      })

      describe('reset', () => {
        describe('when single categorie', () => {
          it('should reset filters and trigger search to Algolia with given category', () => {
            // given
            props.history = createBrowserHistory()
            jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
            })
            props.history.location.pathname = '/recherche-offres/resultats/filtres'
            props.initialFilters = {
              offerCategories: ['VISITE'],
              isSearchAroundMe: true,
              offerTypes: {
                isDigital: false,
                isEvent: false,
                isThing: false
              },
              sortCriteria: '_by_price'
            }
            props.query.parse.mockReturnValue({
              'mots-cles': 'librairie',
            })
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = mount(
              <Router history={props.history}>
                <Filters {...props} />
              </Router>
            )
            const resetButton = wrapper
              .find(HeaderContainer)
              .find('.reset-button')
              .first()

            // when
            resetButton.simulate('click')

            // then
            expect(fetchAlgolia).toHaveBeenCalledWith({
              categories: ['VISITE'],
              geolocationCoordinates: { latitude: 40, longitude: 41 },
              indexSuffix: '_by_price',
              keywords: 'librairie',
              offerTypes: {
                isDigital: false,
                isEvent: false,
                isThing: false
              },
              page: 0
            })
          })
        })
        describe('when multiple categories', () => {
          it('should reset filters and trigger search to Algolia with given categories', () => {
            // given
            props.history = createBrowserHistory()
            jest.spyOn(props.history, 'replace').mockImplementationOnce(() => {
            })
            props.history.location.pathname = '/recherche-offres/resultats/filtres'
            props.initialFilters = {
              offerCategories: ['VISITE', 'CINEMA'],
              isSearchAroundMe: true,
              offerTypes: {
                isDigital: true,
                isEvent: true,
                isThing: true
              },
              sortCriteria: '_by_price'
            }
            props.query.parse.mockReturnValue({
              'mots-cles': 'librairie',
            })
            fetchAlgolia.mockReturnValue(
              new Promise(resolve => {
                resolve({
                  hits: [],
                  nbHits: 0,
                  page: 0,
                })
              })
            )
            const wrapper = mount(
              <Router history={props.history}>
                <Filters {...props} />
              </Router>
            )
            const resetButton = wrapper
              .find(HeaderContainer)
              .find('.reset-button')
              .first()

            // when
            resetButton.simulate('click')

            // then
            expect(fetchAlgolia).toHaveBeenCalledWith({
              categories: ['VISITE', 'CINEMA'],
              geolocationCoordinates: { latitude: 40, longitude: 41 },
              indexSuffix: '_by_price',
              keywords: 'librairie',
              offerTypes: {
                isDigital: false,
                isEvent: false,
                isThing: false
              },
              page: 0,
            })
          })
        })
      })

      describe('offer type', () => {
        it('should display a "Type d\'offres" title for offer types filter', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const title = wrapper.findWhere(node => node.text() === "Type d'offres").first()
          expect(title).toHaveLength(1)
        })

        it('should render three FilterCheckbox components unchecked by default', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes = {
            isDigital: false,
            isEvent: false,
            isThing: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)
          wrapper.setState({ areCategoriesVisible: false })

          // then
          const filterCheckboxes = wrapper.find(FilterCheckbox)
          expect(filterCheckboxes).toHaveLength(3)
          expect(filterCheckboxes.at(0).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(0).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(0).prop('id')).toBe('isDigital')
          expect(filterCheckboxes.at(0).prop('label')).toBe('Offres numériques')
          expect(filterCheckboxes.at(0).prop('name')).toBe('isDigital')
          expect(filterCheckboxes.at(0).prop('onChange')).toStrictEqual(expect.any(Function))
          expect(filterCheckboxes.at(1).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(1).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(1).prop('id')).toBe('isThing')
          expect(filterCheckboxes.at(1).prop('label')).toBe('Offres physiques')
          expect(filterCheckboxes.at(1).prop('name')).toBe('isThing')
          expect(filterCheckboxes.at(1).prop('onChange')).toStrictEqual(expect.any(Function))
          expect(filterCheckboxes.at(2).prop('checked')).toBe(false)
          expect(filterCheckboxes.at(2).prop('className')).toBe('fc-label')
          expect(filterCheckboxes.at(2).prop('id')).toBe('isEvent')
          expect(filterCheckboxes.at(2).prop('label')).toBe('Sorties')
          expect(filterCheckboxes.at(2).prop('name')).toBe('isEvent')
          expect(filterCheckboxes.at(2).prop('onChange')).toStrictEqual(expect.any(Function))
        })

        it('should render three FilterCheckbox components checked when offer filters are checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes = {
            isDigital: true,
            isEvent: true,
            isThing: true,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)
          wrapper.setState({ areCategoriesVisible: false })

          // then
          const filterCheckboxes = wrapper.find(FilterCheckbox)
          expect(filterCheckboxes.at(0).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(0).prop('className')).toBe('fc-label-checked')
          expect(filterCheckboxes.at(1).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(1).prop('className')).toBe('fc-label-checked')
          expect(filterCheckboxes.at(2).prop('checked')).toBe(true)
          expect(filterCheckboxes.at(2).prop('className')).toBe('fc-label-checked')
        })

        it('should display the number of offer types selected when filters are checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes = {
            isDigital: true,
            isEvent: true,
            isThing: true,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.findWhere(node => node.text() === '(3)').first()
          expect(numberOfOfferTypesSelected).toHaveLength(1)
        })

        it('should not display the number of offer types selected when filters are not checked', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerTypes = {
            isDigital: false,
            isEvent: false,
            isThing: false,
          }

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper.findWhere(node => node.text() === '(3)').first()
          expect(numberOfOfferTypesSelected).toHaveLength(0)
        })

        it('should fetch offer when checking digital filter', () => {
          // Given
          props.history.location.pathname = '/recherche-offres/filtres'
          const wrapper = shallow(<Filters {...props} />)
          const digitalFilter = wrapper
            .find('[data-test="sf-offer-types-filter-wrapper"]')
            .find(FilterCheckbox).at(0)
          props.query.parse.mockReturnValue({
            'mots-cles': 'librairies'
          })
          fetchAlgolia.mockReturnValue(
            new Promise(resolve => {
              resolve({
                hits: [],
                nbHits: 0,
                page: 0,
              })
            })
          )

          // When
          digitalFilter.simulate('change', {
            target: {
              name: 'isDigital',
              checked: true
            }
          })

          // Then
          expect(fetchAlgolia).toHaveBeenCalledWith({
            categories: ["VISITE", "CINEMA"],
            geolocationCoordinates: null,
            indexSuffix: "_by_price",
            keywords: "librairies",
            offerTypes: {
              isDigital: true,
              isEvent: false,
              isThing: false
            },
            page: 0
          })
        })
      })

      describe('offer categories', () => {
        it('should display an accessible "Catégories" title button for offer categories filter', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const categoriesTitle = wrapper.find({ children: 'Catégories' })
          const categoriesTitleButton = wrapper.find('button[aria-label="Afficher les catégories"]')
          expect(categoriesTitle).toHaveLength(1)
          expect(categoriesTitleButton.prop('aria-label')).toBe('Afficher les catégories')
          expect(categoriesTitleButton.prop('aria-pressed')).toBe(true)
        })

        it('should not render FilterCheckbox component when categories filter toggled hidden', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = []
          const wrapper = shallow(<Filters {...props} />)
          const categoriesButton = wrapper.findWhere(node => node.text() === 'Catégories').first()
          const categoriesWrapper = wrapper.find('[data-test="sf-categories-filter-wrapper"]')
          const filterCheckboxBeforeClick = categoriesWrapper.find(FilterCheckbox)
          const categoriesButtonClassNameBeforeClick = categoriesButton.prop('className')

          // when
          categoriesButton.simulate('click')

          // then
          const categoriesWrapperAfterClick = wrapper.find(
            '[data-test="sf-categories-filter-wrapper"]'
          )
          const filterCheckboxAfterClick = categoriesWrapperAfterClick.find(FilterCheckbox)
          expect(filterCheckboxBeforeClick).toHaveLength(11)
          expect(filterCheckboxAfterClick).toHaveLength(0)

          const categoriesButtonAfterClick = wrapper
            .findWhere(node => node.text() === 'Catégories')
            .at(1)
          expect(categoriesButtonClassNameBeforeClick).toBe('sf-title-wrapper sf-title-drop-down')
          expect(categoriesButtonAfterClick.prop('className')).toBe(
            'sf-title-wrapper sf-title-drop-down-flipped'
          )
        })

        it('should render one unchecked FilterCheckbox component for each Category Criteria when no category is selected', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaFilterCheckbox = wrapper.find('FilterCheckbox[label="Cinéma"]')
          expect(cinemaFilterCheckbox.prop('checked')).toBe(false)
          expect(cinemaFilterCheckbox.prop('className')).toBe('fc-label')
          expect(cinemaFilterCheckbox.prop('id')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('label')).toBe('Cinéma')
          expect(cinemaFilterCheckbox.prop('name')).toBe('CINEMA')
          expect(cinemaFilterCheckbox.prop('onChange')).toStrictEqual(expect.any(Function))
          expect(wrapper.find('FilterCheckbox[label="Visites, expositions"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Cours, ateliers"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Films, séries, podcasts"]').prop('checked')
          ).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Jeux vidéos"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Conférences, rencontres"]').prop('checked')
          ).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Instruments de musique"]').prop('checked')
          ).toBe(false)
        })

        it('should not render FilterCheckbox component for "Toutes les catégories" Criteria', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const allCategoriesFilterCheckbox = wrapper.find(
            'FilterCheckbox[label="Toutes les catégories"]'
          )
          expect(allCategoriesFilterCheckbox).toHaveLength(0)
        })

        it('should render a FilterCheckbox component checked when category is selected', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'LIVRE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const cinemaCheckbox = wrapper.find('FilterCheckbox[label="Cinéma"]')
          expect(cinemaCheckbox.prop('checked')).toBe(true)
          expect(cinemaCheckbox.prop('className')).toBe('fc-label-checked')
          expect(wrapper.find('FilterCheckbox[label="Visites, expositions"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Musique"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Spectacles"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Cours, ateliers"]').prop('checked')).toBe(
            false
          )
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('checked')).toBe(true)
          expect(wrapper.find('FilterCheckbox[label="Livres"]').prop('className')).toBe(
            'fc-label-checked'
          )
          expect(
            wrapper.find('FilterCheckbox[label="Films, séries, podcasts"]').prop('checked')
          ).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Presse"]').prop('checked')).toBe(false)
          expect(wrapper.find('FilterCheckbox[label="Jeux vidéos"]').prop('checked')).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Conférences, rencontres"]').prop('checked')
          ).toBe(false)
          expect(
            wrapper.find('FilterCheckbox[label="Instruments de musique"]').prop('checked')
          ).toBe(false)
        })

        it('should display the number of selected categories', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'LIVRE', 'VISITE']

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper
            .findWhere(node => node.text() === '(3)')
            .first()
          expect(numberOfOfferTypesSelected).toHaveLength(1)
        })

        it('should not display the number of offer types selected when no filter is selected', () => {
          // given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = []

          // when
          const wrapper = shallow(<Filters {...props} />)

          // then
          const numberOfOfferTypesSelected = wrapper
            .findWhere(node => node.text() === '(0)')
            .first()
          expect(numberOfOfferTypesSelected).toHaveLength(0)
        })

        it('should transform array of categories received from props into an object in state', () => {
          // Given
          props.history.location.pathname = '/recherche-offres/filtres'
          props.initialFilters.offerCategories = ['CINEMA', 'VISITE']

          // When
          const wrapper = shallow(<Filters {...props} />)

          // Then
          expect(wrapper.state().filters.offerCategories).toStrictEqual({
            CINEMA: true,
            VISITE: true,
          })
        })
      })
    })
  })
})
