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
    return (
      <div className={styles['container']}>
        <TextInput
          spellCheck={false}
          autoComplete="off"
          ref={ref}
          {...props}
          type="search"
          icon={strokeSearchIcon}
        />
      </div>
    )
  }
)

SearchInput.displayName = 'SearchInput'
