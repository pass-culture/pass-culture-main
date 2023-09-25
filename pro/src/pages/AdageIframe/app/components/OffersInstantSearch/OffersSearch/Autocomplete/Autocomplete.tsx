import {
  createAutocomplete,
  AutocompleteState,
} from '@algolia/autocomplete-core'
import { createQuerySuggestionsPlugin } from '@algolia/autocomplete-plugin-query-suggestions'
import { AutocompleteQuerySuggestionsHit } from '@algolia/autocomplete-plugin-query-suggestions/dist/esm/types'
import { createLocalStorageRecentSearchesPlugin } from '@algolia/autocomplete-plugin-recent-searches'
import algoliasearch from 'algoliasearch/lite'
import cn from 'classnames'
import React, {
  useState,
  useMemo,
  BaseSyntheticEvent,
  MouseEvent,
  KeyboardEvent,
  useEffect,
  useRef,
} from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import useActiveFeature from 'hooks/useActiveFeature'
import fullClearIcon from 'icons/full-clear.svg'
import strokeBuildingIcon from 'icons/stroke-building.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import styles from './Autocomplete.module.scss'

type AutocompleteProps = SearchBoxProvided & {
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
}

const ALGOLIA_NUMBER_RECENT_SEARCHES = 5
const ALGOLIA_NUMBER_VENUES_SUGGESTIONS = 6
const DEFAULT_GEO_RADIUS = 30000000 // 30 000 km ensure that we get all the results

const AutocompleteComponent = ({
  refine,
  initialQuery,
  placeholder,
  setCurrentSearch,
}: AutocompleteProps) => {
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

  const isRecentSearchEnabled = useActiveFeature(
    'WIP_ENABLE_SEARCH_HISTORY_ADAGE'
  )
  const RECENT_SEARCH_SOURCE_ID = 'RecentSearchSource'
  const VENUE_SUGGESTIONS_SOURCE_ID = 'VenueSuggestionsSource'
  const adageUser = useAdageUser()

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
          autocomplete.setQuery(item.venue.publicName || item.venue.name)
          refine(item.venue.publicName || item.venue.name)
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
        plugins: isRecentSearchEnabled
          ? [recentSearchesPlugin, venuesSuggestionsPlugin]
          : [],
      }),
    [placeholder, refine]
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
    instantSearchUiState.collections.find(
      x => x.source.sourceId === RECENT_SEARCH_SOURCE_ID
    ) || {
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
  const shouldDisplayVenueSuggestions =
    isRecentSearchEnabled &&
    venuesSuggestionsSource &&
    venuesSuggestionsItems &&
    venuesSuggestionsItems.length > 0 &&
    !!instantSearchUiState.query

  const shouldDisplayHistory =
    isRecentSearchEnabled && recentSearchesSource && !instantSearchUiState.query
  return (
    <div>
      {instantSearchUiState.isOpen && (
        <div className={styles['backdrop']}></div>
      )}
      <div {...autocomplete.getRootProps({})}>
        <form
          ref={formRef}
          className={styles['form']}
          {...autocomplete.getFormProps({ inputElement: inputRef.current })}
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

              <Button
                type="submit"
                className={styles['form-search-button']}
                // TODO: delete when the link is added
                onBlur={() => {
                  if (shouldDisplayHistory) {
                    return
                  }
                  autocomplete.setIsOpen(false)
                }}
                onMouseDown={e => {
                  // avoids onfocus code when "Rechercher" is clicked
                  e.preventDefault()
                }}
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
                className={cn(styles['dialog-panel'], {
                  [styles['dialog-panel-hide']]:
                    instantSearchUiState.collections.length < 1,
                })}
                {...autocomplete.getPanelProps({})}
              >
                {shouldDisplayHistory && (
                  <div
                    key={`recent-search`}
                    className={styles['dialog-panel-autocomplete']}
                  >
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
                            'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH'
                          )
                          autocomplete.refresh()
                        }}
                        // TODO: delete when the link is added
                        onBlur={() => {
                          autocomplete.setIsOpen(false)
                        }}
                      >
                        Effacer
                      </Button>
                    </span>
                    {recentSearchesItems && recentSearchesItems.length > 0 && (
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
                    )}
                  </div>
                )}
                {shouldDisplayVenueSuggestions && (
                  <div
                    key={`venue-suggestions`}
                    className={styles['dialog-panel-autocomplete']}
                  >
                    <span className={styles['dialog-panel-autocomplete-text']}>
                      Partenaires culturels
                    </span>

                    <ul
                      className={styles['dialog-panel-autocomplete-list']}
                      {...autocomplete.getListProps()}
                    >
                      {venuesSuggestionsItems
                        .sort((a, b) =>
                          (a.venue.publicName || a.venue.name).localeCompare(
                            b.venue.publicName || b.venue.name
                          )
                        )
                        .map(item => (
                          <li
                            key={`item-${item.objectID}`}
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
                            {item.venue.publicName || item.venue.name}
                          </li>
                        ))}
                    </ul>
                  </div>
                )}
              </div>
              {/* TODO : uncomment when the link is added */}
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

export const Autocomplete = connectSearchBox<AutocompleteProps>(
  AutocompleteComponent
)
