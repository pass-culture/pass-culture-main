import {
  createAutocomplete,
  AutocompleteState,
} from '@algolia/autocomplete-core'
import { createLocalStorageRecentSearchesPlugin } from '@algolia/autocomplete-plugin-recent-searches'
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
import fullLinkIcon from 'icons/full-link.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Autocomplete.module.scss'

type AutocompleteItem = {
  label: string
}

type AutocompleteProps = SearchBoxProvided & {
  initialQuery: string
  placeholder: string
}

const ALGOLIA_NUMBER_SEARCHES = 5

const AutocompleteComponent = ({
  refine,
  initialQuery,
  placeholder,
}: AutocompleteProps) => {
  const [instantSearchUiState, setInstantSearchUiState] = useState<
    AutocompleteState<AutocompleteItem>
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

  const recentSearchesPlugin = createLocalStorageRecentSearchesPlugin({
    key: 'RECENT_SEARCH',
    limit: ALGOLIA_NUMBER_SEARCHES,
  })

  const autocomplete = useMemo(
    () =>
      createAutocomplete<
        AutocompleteItem,
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
        },
        placeholder,
        plugins: isRecentSearchEnabled ? [recentSearchesPlugin] : [],
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

              <Button type="submit" className={styles['form-search-button']}>
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
                {instantSearchUiState.collections.map((collection, index) => {
                  const { source, items } = collection
                  return (
                    isRecentSearchEnabled && (
                      <div
                        key={`recent-search-${index}`}
                        className={styles['dialog-panel-recent-search']}
                      >
                        <span
                          className={styles['dialog-panel-recent-search-text']}
                        >
                          Recherches récentes
                          <Button
                            className={
                              styles['dialog-panel-recent-search-text-clean']
                            }
                            variant={ButtonVariant.QUATERNARYPINK}
                            icon={fullClearIcon}
                            onClick={() => {
                              localStorage.removeItem(
                                'AUTOCOMPLETE_RECENT_SEARCHES:RECENT_SEARCH'
                              )
                              autocomplete.refresh()
                            }}
                          >
                            Effacer
                          </Button>
                        </span>
                        {items && items.length > 0 && (
                          <ul
                            className={
                              styles['dialog-panel-recent-search-list']
                            }
                            {...autocomplete.getListProps()}
                          >
                            {items.map((item, index) => (
                              <li
                                key={`item-${index}`}
                                className={
                                  styles['dialog-panel-recent-search-item']
                                }
                                {...autocomplete.getItemProps({
                                  item,
                                  source,
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
                    )
                  )
                })}
              </div>
              <div
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
              </div>
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
