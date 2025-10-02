import strokeSearchIcon from 'icons/stroke-search.svg'
import { type ForwardedRef, forwardRef } from 'react'

import { TextInput, type TextInputProps } from '../TextInput/TextInput'
import styles from './SearchInput.module.scss'

export type SearchInputProps = Omit<
  TextInputProps,
  'icon' | 'iconButton' | 'type'
>

export const SearchInput = forwardRef(
  (props: SearchInputProps, ref: ForwardedRef<HTMLInputElement>) => {
    function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
      if (event.key === 'Escape') {
        //  In case the search input is in a dropdown or in a modal
        event.stopPropagation()
      }
    }

    return (
      <div className={styles['container']}>
        <TextInput
          spellCheck={false}
          autoComplete="off"
          ref={ref}
          onKeyDown={handleKeyDown}
          {...props}
          type="search"
          icon={strokeSearchIcon}
        />
      </div>
    )
  }
)

SearchInput.displayName = 'SearchInput'
