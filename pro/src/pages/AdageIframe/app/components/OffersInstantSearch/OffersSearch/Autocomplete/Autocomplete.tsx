import { createAutocomplete } from '@algolia/autocomplete-core'
import React, {
  useState,
  useMemo,
  BaseSyntheticEvent,
  MouseEvent,
  KeyboardEvent,
} from 'react'

import strokeSearch from 'icons/stroke-search.svg'
import { Button } from 'ui-kit'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Autocomplete.module.scss'

type SetInstantSearchUiStateOptions = {
  query: string
}

export function Autocomplete({
  placeholder,
  refine,
}: {
  placeholder: string
  refine: (...args: any[]) => any
}) {
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
        onReset: () => {
          console.log('reset')
          setInstantSearchUiState({ query: '' })
          refine('')
        },
        placeholder,
      }),
    [placeholder, refine]
  )

  const inputRef = React.useRef<HTMLInputElement>(null)
  const formRef = React.useRef<HTMLFormElement>(null)

  return (
    <div className="aa-Autocomplete" {...autocomplete.getRootProps({})}>
      <form
        ref={formRef}
        className="aa-Form"
        {...autocomplete.getFormProps({ inputElement: inputRef.current })}
      >
        <div className={styles['aa-InputWrapper']}>
          <div className={styles['aa-InputContainer']}>
            <input
              className={styles['aa-Input']}
              ref={inputRef}
              {...autocomplete.getInputProps({
                inputElement: inputRef.current,
              })}
            />
            <span
              className={styles['aa-Span']}
              {...autocomplete.getLabelProps({})}
            >
              <SvgIcon src={strokeSearch} alt="Rechercher" width="16" />
            </span>
          </div>

          <Button type="submit" className={styles['aa-SearchButton']}>
            Rechercher
          </Button>
        </div>
      </form>
    </div>
  )
}
