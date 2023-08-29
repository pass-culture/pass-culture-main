import { createAutocomplete } from '@algolia/autocomplete-core'
import React, {
  useState,
  useMemo,
  BaseSyntheticEvent,
  MouseEvent,
  KeyboardEvent,
  useEffect,
} from 'react'
import type { SearchBoxProvided } from 'react-instantsearch-core'
import { connectSearchBox } from 'react-instantsearch-dom'

import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Autocomplete.module.scss'

type SetInstantSearchUiStateOptions = {
  query: string
}

type AutocompleteProps = SearchBoxProvided & {
  initialQuery: string
  placeholder: string
}

const AutocompleteComponent = ({
  refine,
  initialQuery,
  placeholder,
}: AutocompleteProps) => {
  const [, setInstantSearchUiState] = useState({
    query: '',
  })

  const autocomplete = useMemo(
    () =>
      createAutocomplete<
        SetInstantSearchUiStateOptions,
        BaseSyntheticEvent,
        MouseEvent,
        KeyboardEvent
      >({
        onStateChange: ({ state }) => {
          setInstantSearchUiState(state)
        },
        insights: true,
        onSubmit: ({ state }) => {
          refine(state.query)
        },
        placeholder: placeholder,
      }),
    [placeholder, refine]
  )

  useEffect(() => {
    autocomplete.setQuery(initialQuery)
    refine(initialQuery)
  }, [initialQuery])

  const inputRef = React.useRef<HTMLInputElement>(null)
  const formRef = React.useRef<HTMLFormElement>(null)

  return (
    <div className="aa-autocomplete" {...autocomplete.getRootProps({})}>
      <form
        ref={formRef}
        className="aa-form"
        {...autocomplete.getFormProps({ inputElement: inputRef.current })}
      >
        <div className={styles['aa-inputwrapper']}>
          <div className={styles['aa-inputcontainer']}>
            <input
              className={styles['aa-input']}
              ref={inputRef}
              {...autocomplete.getInputProps({
                inputElement: inputRef.current,
              })}
            />
            <span
              className={styles['aa-span']}
              {...autocomplete.getLabelProps({})}
            >
              <SvgIcon src={strokeSearchIcon} alt="Rechercher" width="16" />
            </span>
          </div>

          <Button type="submit" className={styles['aa-searchbutton']}>
            Rechercher
          </Button>
        </div>
      </form>
    </div>
  )
}

export const Autocomplete = connectSearchBox<AutocompleteProps>(
  AutocompleteComponent
)
