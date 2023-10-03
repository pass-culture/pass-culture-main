import {
  createAutocomplete,
  AutocompleteState,
} from '@algolia/autocomplete-core'
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions'
import { AutocompleteQuerySuggestionsHit } from '@algolia/autocomplete-plugin-query-suggestions/dist/esm/types'
import { createLocalStorageRecentSearchesPlugin } from '@algolia/autocomplete-plugin-recent-searches'
import algoliasearch from 'algoliasearch/lite'
import { FormikContext } from 'formik'
import React, {
  useState,
  useMemo,
  BaseSyntheticEvent,
  MouseEvent,
  KeyboardEvent,
  useEffect,
  useRef,
  useContext,
} from 'react'
import { useSearchBox } from 'react-instantsearch'

import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import fullClearIcon from 'icons/full-clear.svg'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { getEducationalCategoriesOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalCategoriesOptionsAdapter'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { Option } from 'pages/AdageIframe/app/types'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
  ALGOLIA_COLLECTIVE_OFFERS_SUGGESTIONS_INDEX,
} from 'utils/config'

import styles from './Autocomplete.module.scss'
import { Highlight } from './Highlight'

type AutocompleteProps = {
  initialQuery: string
  placeholder: string
  setCurrentSearch: (search: string) => void
}

export type SuggestionItem = AutocompleteQuerySuggestionsHit & {
  label: string
  venue: {
    name: string
    publicName: string
  }
  offerer: {
    name: string
  }
  ['offer.subcategoryId']: string[]
}

const ALGOLIA_NUMBER_RECENT_SEARCHES = 5
const ALGOLIA_NUMBER_VENUES_SUGGESTIONS = 6
const DEFAULT_GEO_RADIUS = 30000000 // 30 000 km ensure that we get all the results
const ALGOLIA_NUMBER_QUERY_SUGGESTIONS = 5
const AUTOCOMPLETE_LOCAL_STORAGE_KEY =
  'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH'

const addSuggestionToHistory = (suggestion: string) => {
  const currentHistory = localStorage.getItem(AUTOCOMPLETE_LOCAL_STORAGE_KEY)
  const currentHistoryParsed = currentHistory ? JSON.parse(currentHistory) : []
  if (
    !currentHistoryParsed.find((item: { id: string }) => item.id === suggestion)
  ) {
    currentHistoryParsed.unshift({ id: suggestion, label: suggestion })
  }

  localStorage.setItem(
    AUTOCOMPLETE_LOCAL_STORAGE_KEY,
    JSON.stringify(currentHistoryParsed)
  )
}

export const Autocomplete = ({
  initialQuery,
  placeholder,
  setCurrentSearch,
}: AutocompleteProps) => {
  const { refine } = useSearchBox()
  const [instantSearchUiState, setInstantSearchUiState] = useState<
    AutocompleteState<SuggestionItem>
  >({
    collections: [],
    completion: null,
    context: {},
    isOpen: false,
    query: '',
    activeItemId: null,
    status: 'idle',
  })
  const inputRef = useRef<HTMLInputElement>(null)
  const formRef = useRef<HTMLFormElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const enableAutocompleteAdage = useActiveFeature(
    'WIP_ENABLE_SEARCH_HISTORY_ADAGE'
  )

  const formik = useContext(FormikContext)

  const [categories, setCategories] = useState<Option<string[]>[]>([])
  const notify = useNotification()

  const RECENT_SEARCH_SOURCE_ID = 'RecentSearchSource'
  const VENUE_SUGGESTIONS_SOURCE_ID = 'VenueSuggestionsSource'
  const { adageUser } = useAdageUser()
  const KEYWORD_QUERY_SUGGESTIONS_SOURCE_ID = 'KeywordQuerySuggestionsSource'
  useEffect(() => {
    const loadData = async () => {
      const categoriesResponse =
        await getEducationalCategoriesOptionsAdapter(null)

      if (!categoriesResponse.isOk) {
        return notify.error(categoriesResponse.message)
      }

      setCategories(categoriesResponse.payload.educationalCategories)
    }

    // TODO: delete when ff deleted
    enableAutocompleteAdage && loadData()
  }, [])

  // retrieves recent searches made in the search input
  const recentSearchesPlugin = createLocalStorageRecentSearchesPlugin({
    key: 'RECENT_SEARCH',
    limit: ALGOLIA_NUMBER_RECENT_SEARCHES,
    transformSource({ source }) {
      return {
        ...source,
        sourceId: RECENT_SEARCH_SOURCE_ID,
        onSelect({ item }) {
          refine(item.label)
        },
      }
    },
  })

  const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

  // provides search suggestions based on existing partners
  /* istanbul ignore next: We dont want to test algolia implementation */
  const venuesSuggestionsPlugin = createQuerySuggestionsPlugin<SuggestionItem>({
    searchClient: searchClient,
    indexName: ALGOLIA_COLLECTIVE_OFFERS_INDEX,
    getSearchParams() {
      return {
        restrictSearchableAttributes: [
          'venue.name',
          'venue.publicName',
          'offerer.name',
        ],
        facetFilters: [
          [
            'offer.educationalInstitutionUAICode:all',
            `offer.educationalInstitutionUAICode:${adageUser.uai}`,
          ],
        ],
        distinct: true,
        hitsPerPage: ALGOLIA_NUMBER_VENUES_SUGGESTIONS,
        clickAnalytics: false,
        aroundLatLng:
          adageUser.lat && adageUser.lon
            ? `${adageUser.lat}, ${adageUser.lon}`
            : '',
        aroundRadius: DEFAULT_GEO_RADIUS,
      }
    },
    transformSource({ source }) {
      return {
        ...source,
        sourceId: VENUE_SUGGESTIONS_SOURCE_ID,
        onSelect({ item }) {
          const venueDisplayName = item.venue.publicName || item.venue.name
          autocomplete.setQuery(venueDisplayName)
          refine(venueDisplayName)
          addSuggestionToHistory(venueDisplayName)
        },
        getItems(params) {
          if (!params.state.query) {
            return []
          }

          return source.getItems(params)
        },
        templates: {
          item({ item }) {
            return item.venue.publicName || item.venue.name
          },
        },
      }
    },
  })

  // retrieves search-based suggestions from an index that generates suggestions based on existing offers
  const querySuggestionsPlugin = createQuerySuggestionsPlugin<SuggestionItem>({
    searchClient,
    indexName: ALGOLIA_COLLECTIVE_OFFERS_SUGGESTIONS_INDEX,
    getSearchParams() {
      return {
        hitsPerPage: ALGOLIA_NUMBER_QUERY_SUGGESTIONS,
      }
    },
    transformSource({ source }) {
      return {
        ...source,
        sourceId: KEYWORD_QUERY_SUGGESTIONS_SOURCE_ID,
        getItems(params) {
          if (!params.state.query) {
            return []
          }

          return source.getItems(params)
        },
        async onSelect(params) {
          const { item, source: sourceTmp } = params

          const items = (await sourceTmp.getItems({
            ...params,
            query: params.state.query,
          })) as SuggestionItem[]

          const itemId = items.findIndex(elm => elm.objectID === item.objectID)

          // if the id is less than 3, the category is displayed and must be pre-selected in the filters.
          if (
            itemId >= 0 &&
            itemId < 3 &&
            item['offer.subcategoryId'] &&
            item['offer.subcategoryId'].length > 0
          ) {
            const result = getCategoriesFromSubcategory(
              item['offer.subcategoryId'][0]
            )

            result && formik.setFieldValue('categories', [result.subCategories])
          } else {
            formik.setFieldValue('categories', [])
          }
          refine(item.query)
          formik.submitForm()
          addSuggestionToHistory(item.query)
        },
      }
    },
  })

  const autocomplete = useMemo(
    () =>
      createAutocomplete<
        SuggestionItem,
        BaseSyntheticEvent,
        MouseEvent,
        KeyboardEvent
      >({
        initialState: instantSearchUiState,
        insights: true,
        openOnFocus: true,
        onStateChange: ({ state }) => {
          setInstantSearchUiState(state)
        },
        onSubmit: ({ state }) => {
          refine(state.query)
          setCurrentSearch(state.query)
        },
        placeholder,
        plugins: enableAutocompleteAdage
          ? [
              recentSearchesPlugin,
              venuesSuggestionsPlugin,
              querySuggestionsPlugin,
            ]
          : [],
      }),
    [placeholder, refine, categories]
  )

  useEffect(() => {
    autocomplete.setQuery(initialQuery)
    refine(initialQuery)
  }, [initialQuery])

  const { getEnvironmentProps } = autocomplete

  useEffect(() => {
    /* istanbul ignore next: ref initialized to null but they are always present */
    if (!formRef.current || !panelRef.current || !inputRef.current) {
      return undefined
    }

    // As long as you click on the items ref below, the panel remains open.
    const { onTouchStart, onTouchMove, onMouseDown } = getEnvironmentProps({
      formElement: formRef.current,
      inputElement: inputRef.current,
      panelElement: panelRef.current,
    })

    window.addEventListener('mousedown', onMouseDown)
    window.addEventListener('touchstart', onTouchStart)
    window.addEventListener('touchmove', onTouchMove)

    return () => {
      window.removeEventListener('mousedown', onMouseDown)
      window.removeEventListener('touchstart', onTouchStart)
      window.removeEventListener('touchmove', onTouchMove)
    }
  }, [getEnvironmentProps, instantSearchUiState.isOpen])

  const { source: recentSearchesSource, items: recentSearchesItems } =
    (!instantSearchUiState.query &&
      instantSearchUiState.collections.find(
        x => x.source.sourceId === RECENT_SEARCH_SOURCE_ID
      )) || {
      source: null,
      items: [],
    }

  const { source: venuesSuggestionsSource, items: venuesSuggestionsItems } =
    instantSearchUiState.collections.find(
      x => x.source.sourceId === VENUE_SUGGESTIONS_SOURCE_ID
    ) || {
      source: null,
      items: [],
    }

  const { source: keywordSuggestionsSource, items: keywordSuggestionsItems } =
    instantSearchUiState.collections.find(
      x => x.source.sourceId === KEYWORD_QUERY_SUGGESTIONS_SOURCE_ID
    ) || {
      source: null,
      items: [],
    }

  const getCategoriesFromSubcategory = (subCategory: string) => {
    const result = categories?.find(objet => objet.value.includes(subCategory))

    return { label: result?.label, subCategories: result?.value }
  }

  const shouldDisplayRecentSearch =
    enableAutocompleteAdage &&
    recentSearchesSource &&
    recentSearchesItems &&
    recentSearchesItems.length > 0 &&
    Boolean(!instantSearchUiState.query)

  const shouldDisplayVenueSuggestions =
    enableAutocompleteAdage &&
    venuesSuggestionsSource &&
    venuesSuggestionsItems &&
    venuesSuggestionsItems.length > 0 &&
    Boolean(instantSearchUiState.query)

  const shouldDisplayKeywordSuggestions =
    enableAutocompleteAdage &&
    keywordSuggestionsSource &&
    keywordSuggestionsItems &&
    keywordSuggestionsItems.length > 0 &&
    Boolean(instantSearchUiState.query)

  return (
    <div>
      {instantSearchUiState.isOpen && (
        <div className={styles['backdrop']}></div>
      )}
      <div {...autocomplete.getRootProps({})}>
        <form
          ref={formRef}
          className={styles['form']}
          {...autocomplete.getFormProps({
            inputElement: inputRef.current,
          })}
          onFocus={e => {
            // Accessibility : if the focus element is part of the form and there are results, leave the panel open, otherwise close it
            if (
              formRef.current?.contains(e.target) &&
              instantSearchUiState.collections.length > 0
            ) {
              autocomplete.setIsOpen(true)
            }
          }}
          onKeyDown={e => {
            if (e.code === 'Escape') {
              autocomplete.setIsOpen(false)
            }
          }}
        >
          <div className={styles['form-container']}>
            <div className={styles['form-container-wrapper']}>
              <div className={styles['form-container-input']}>
                <input
                  className={styles['form-input']}
                  ref={inputRef}
                  {...autocomplete.getInputProps({
                    inputElement: inputRef.current,
                  })}
                />
                <span
                  className={styles['form-input-span']}
                  {...autocomplete.getLabelProps({})}
                >
                  <SvgIcon src={strokeSearchIcon} alt="Rechercher" width="16" />
                </span>
              </div>

              <SubmitButton
                // TODO: delete when the link is added
                onBlur={() => {
                  if (shouldDisplayRecentSearch) {
                    return
                  }
                  autocomplete.setIsOpen(false)
                }}
                onMouseDown={e => {
                  // avoids onfocus code when "Rechercher" is clicked
                  e.preventDefault()
                }}
                className={styles['form-search-button']}
              >
                Rechercher
              </SubmitButton>
            </div>

            <dialog
              data-testid="dialog"
              className={styles['dialog']}
              open={instantSearchUiState.isOpen}
            >
              <div
                data-testid="dialog-panel"
                ref={panelRef}
                className={styles['dialog-panel']}
                {...autocomplete.getPanelProps({})}
              >
                {shouldDisplayRecentSearch && (
                  <div className={styles['dialog-panel-autocomplete']}>
                    <span className={styles['dialog-panel-autocomplete-text']}>
                      Recherches récentes
                      <Button
                        className={
                          styles['dialog-panel-autocomplete-text-clean']
                        }
                        variant={ButtonVariant.QUATERNARYPINK}
                        icon={fullClearIcon}
                        onClick={() => {
                          localStorage.removeItem(
                            AUTOCOMPLETE_LOCAL_STORAGE_KEY
                          )
                          autocomplete.setIsOpen(false)
                        }}
                        // TODO: delete when the link is added
                        onBlur={() => {
                          autocomplete.setIsOpen(false)
                        }}
                      >
                        Effacer
                      </Button>
                    </span>
                    <ul
                      className={styles['dialog-panel-autocomplete-list']}
                      {...autocomplete.getListProps()}
                    >
                      {recentSearchesItems.map((item, index) => (
                        <li
                          key={`item-${index}`}
                          className={styles['dialog-panel-autocomplete-item']}
                          {...autocomplete.getItemProps({
                            item,
                            source: recentSearchesSource,
                          })}
                        >
                          <SvgIcon
                            src={strokeClockIcon}
                            alt="Récente recherche"
                          />
                          {item.label}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {shouldDisplayVenueSuggestions && (
                  <div className={styles['dialog-panel-autocomplete']}>
                    <span className={styles['dialog-panel-autocomplete-text']}>
                      Partenaires culturels
                    </span>

                    <ul
                      className={styles['dialog-panel-autocomplete-list']}
                      {...autocomplete.getListProps()}
                    >
                      {venuesSuggestionsItems.map((item, index) => (
                        <li
                          key={`item-venue-${index}`}
                          className={styles['dialog-panel-autocomplete-item']}
                          {...autocomplete.getItemProps({
                            item,
                            source: venuesSuggestionsSource,
                          })}
                        >
                          <SvgIcon
                            src={strokeBuildingIcon}
                            alt=""
                            className={
                              styles['dialog-panel-autocomplete-item-icon']
                            }
                          />
                          <div>
                            <Highlight
                              hit={item}
                              attribute={[
                                'venue',
                                item.venue.publicName ? 'publicName' : 'name',
                              ]}
                              tagName="strong"
                            />
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {shouldDisplayKeywordSuggestions && (
                  <div className={styles['dialog-panel-autocomplete']}>
                    <span className={styles['dialog-panel-autocomplete-text']}>
                      Suggestions
                    </span>

                    <ul
                      className={styles['dialog-panel-autocomplete-list']}
                      {...autocomplete.getListProps()}
                    >
                      {keywordSuggestionsItems.map((item, index) => {
                        const shouldDisplayCategory =
                          index <= 2 &&
                          item['offer.subcategoryId'] &&
                          item['offer.subcategoryId'].length > 0
                        return (
                          <li
                            key={`item-keyword-${index}`}
                            className={styles['dialog-panel-autocomplete-item']}
                            {...autocomplete.getItemProps({
                              item,
                              source: keywordSuggestionsSource,
                              id: `keyword-${index}`,
                            })}
                          >
                            <SvgIcon
                              src={strokeSearchIcon}
                              alt=""
                              className={
                                styles['dialog-panel-autocomplete-item-icon']
                              }
                            />
                            <div>
                              <Highlight
                                hit={item}
                                attribute={['query']}
                                tagName="strong"
                              />
                              {shouldDisplayCategory && ' dans '}
                              <span
                                className={
                                  styles['dialog-panel-autocomplete-category']
                                }
                              >
                                {shouldDisplayCategory &&
                                  getCategoriesFromSubcategory(
                                    item['offer.subcategoryId'][0]
                                  ).label}
                              </span>
                            </div>
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}
              </div>
              {/* <div
                className={cn(styles['panel-footer'], {
                  [styles['panel-footer-no-result']]: !localStorage.getItem(
                    'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH'
                  ),
                })}
              >
                <ButtonLink
                  className={styles['panel-footer-link']}
                  variant={ButtonVariant.TERNARYPINK}
                  link={{
                    to: '#', // TODO:  Lien FAQ à ajouter quand il sera disponible
                    isExternal: true,
                  }}
                  icon={fullLinkIcon}
                  onBlur={() => {
                    autocomplete.setIsOpen(false)
                  }}
                >
                  Comment fonctionne la recherche ?
                </ButtonLink>
              </div> */}
            </dialog>
          </div>
        </form>
      </div>
    </div>
  )
}
