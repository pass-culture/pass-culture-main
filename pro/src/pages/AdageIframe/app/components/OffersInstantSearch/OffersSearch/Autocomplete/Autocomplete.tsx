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
import { useDispatch } from 'react-redux'

import { SuggestionType } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import fullClearIcon from 'icons/full-clear.svg'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { setAdageQuery } from 'store/adageFilter/reducer'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
  ALGOLIA_COLLECTIVE_OFFERS_SUGGESTIONS_INDEX,
} from 'utils/config'
import { localStorageAvailable } from 'utils/localStorageAvailable'

import styles from './Autocomplete.module.scss'
import { Highlight } from './Highlight'

type AutocompleteProps = {
  initialQuery: string
  placeholder: string
}

export type SuggestionItem = AutocompleteQuerySuggestionsHit & {
  label: string
  venue: {
    id: string
    name: string
    publicName: string
    departmentCode: string
  }
  offerer: {
    name: string
  }
  formats: string[]
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
}: AutocompleteProps) => {
  const dispatch = useDispatch()

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

  const formik = useContext(FormikContext)

  const RECENT_SEARCH_SOURCE_ID = 'RecentSearchSource'
  const VENUE_SUGGESTIONS_SOURCE_ID = 'VenueSuggestionsSource'
  const { adageUser } = useAdageUser()
  const KEYWORD_QUERY_SUGGESTIONS_SOURCE_ID = 'KeywordQuerySuggestionsSource'

  const isLocalStorageEnabled = localStorageAvailable()

  const logAutocompleteSuggestionClick = async (
    suggestionType: SuggestionType,
    suggestionValue: string
  ) => {
    await apiAdage.logTrackingAutocompleteSuggestionClick({
      iframeFrom: location.pathname,
      suggestionType,
      suggestionValue,
    })
  }

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
        async onSelect({ item }) {
          const venueDisplayName = item.venue.publicName || item.venue.name
          autocomplete.setQuery('')
          refine('')
          dispatch(setAdageQuery(''))
          await formik.setFieldValue('venue', { ...item.venue, relative: [] })
          await formik.submitForm()

          if (isLocalStorageEnabled) {
            addSuggestionToHistory(venueDisplayName)
          }

          await logAutocompleteSuggestionClick(
            SuggestionType.VENUE,
            venueDisplayName
          )
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

          const itemId = items.findIndex(
            (elm) => elm.objectID === item.objectID
          )

          if (itemId >= 0 && itemId < 3) {
            await formik.setFieldValue('formats', [item.formats[0]])
          } else {
            await formik.setFieldValue('formats', [])
          }
          refine(item.query)
          await formik.submitForm()

          if (isLocalStorageEnabled) {
            addSuggestionToHistory(item.query)
          }

          void logAutocompleteSuggestionClick(
            itemId <= 2 ? SuggestionType.OFFER_CATEGORY : SuggestionType.OFFER,
            item.query
          )
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
          dispatch(setAdageQuery(state.query))
        },
        placeholder,
        plugins: [
          ...(isLocalStorageEnabled ? [recentSearchesPlugin] : []),
          venuesSuggestionsPlugin,
          querySuggestionsPlugin,
        ],
      }),
    [placeholder, refine, isLocalStorageEnabled]
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
        (x) => x.source.sourceId === RECENT_SEARCH_SOURCE_ID
      )) || {
      source: null,
      items: [],
    }

  const { source: venuesSuggestionsSource, items: venuesSuggestionsItems } =
    instantSearchUiState.collections.find(
      (x) => x.source.sourceId === VENUE_SUGGESTIONS_SOURCE_ID
    ) || {
      source: null,
      items: [],
    }

  const { source: keywordSuggestionsSource, items: keywordSuggestionsItems } =
    instantSearchUiState.collections.find(
      (x) => x.source.sourceId === KEYWORD_QUERY_SUGGESTIONS_SOURCE_ID
    ) || {
      source: null,
      items: [],
    }

  const shouldDisplayRecentSearch =
    recentSearchesSource &&
    recentSearchesItems.length > 0 &&
    Boolean(!instantSearchUiState.query)

  const shouldDisplayVenueSuggestions =
    venuesSuggestionsSource &&
    venuesSuggestionsItems.length > 0 &&
    Boolean(instantSearchUiState.query)

  const shouldDisplayKeywordSuggestions =
    keywordSuggestionsSource &&
    keywordSuggestionsItems.length > 0 &&
    Boolean(instantSearchUiState.query)

  return (
    <div>
      {instantSearchUiState.isOpen && <div className={styles['backdrop']} />}
      <div {...autocomplete.getRootProps({})}>
        <form
          ref={formRef}
          className={styles['form']}
          {...autocomplete.getFormProps({
            inputElement: inputRef.current,
          })}
          onFocus={(e) => {
            // Accessibility : if the focus element is part of the form and there are results, leave the panel open, otherwise close it
            if (
              formRef.current?.contains(e.target) &&
              instantSearchUiState.collections.length > 0
            ) {
              autocomplete.setIsOpen(true)
            }
          }}
          onKeyDown={(e) => {
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
                  <SvgIcon src={strokeSearchIcon} alt="" width="16" />
                </span>
              </div>

              <Button
                type="submit"
                onBlur={() => {
                  if (shouldDisplayRecentSearch) {
                    return
                  }
                  autocomplete.setIsOpen(false)
                }}
                onMouseDown={(e) => {
                  // avoids onfocus code when "Rechercher" is clicked
                  e.preventDefault()
                }}
                className={styles['form-search-button']}
              >
                Rechercher
              </Button>
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
                            width="16"
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
                            width="16"
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
                        let displayValue = null
                        const shouldDisplayFormats =
                          index <= 2 && item.formats.length > 0

                        if (shouldDisplayFormats) {
                          displayValue = item.formats[0]
                        }

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
                              width="16"
                            />
                            <div>
                              <Highlight
                                hit={item}
                                attribute={['query']}
                                tagName="strong"
                              />
                              {shouldDisplayFormats ? ' dans ' : ''}
                              <span
                                className={
                                  styles['dialog-panel-autocomplete-category']
                                }
                              >
                                {displayValue}
                              </span>
                            </div>
                          </li>
                        )
                      })}
                    </ul>
                  </div>
                )}
              </div>
            </dialog>
          </div>
        </form>
      </div>
    </div>
  )
}
