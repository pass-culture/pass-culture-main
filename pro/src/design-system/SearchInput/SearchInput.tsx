import fullClearIcon from 'icons/full-clear.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import {
  type ForwardedRef,
  forwardRef,
  useImperativeHandle,
  useRef,
} from 'react'

import { TextInput, type TextInputProps } from '../TextInput/TextInput'
import styles from './SearchInput.module.scss'

export type SearchInputProps = Omit<
  TextInputProps,
  'icon' | 'iconButton' | 'type'
>

export const SearchInput = forwardRef(
  (props: SearchInputProps, ref: ForwardedRef<HTMLInputElement>) => {
    const inputRef = useRef<HTMLInputElement>(null)

    useImperativeHandle(ref, () => inputRef.current as HTMLInputElement)

    const isClearButtonVisible =
      Boolean(inputRef.current?.value) || Boolean(props.value)

    return (
      <div className={styles['container']}>
        <TextInput
          spellCheck={false}
          autoComplete="off"
          ref={inputRef}
          {...props}
          type="search"
          icon={strokeSearchIcon}
          iconButton={
            isClearButtonVisible && !props.disabled
              ? {
                  icon: fullClearIcon,
                  label: 'Effacer',
                  onClick: () => {
                    const input = inputRef.current
                    if (input) {
                      input.value = ''

                      if (props.onChange) {
                        const syntheticEvent: React.ChangeEvent<HTMLInputElement> =
                          {
                            ...({} as React.ChangeEvent<HTMLInputElement>),
                            target: input,
                            currentTarget: input,
                            type: 'change',
                          }

                        props.onChange(syntheticEvent)
                      }
                    }
                  },
                }
              : undefined
          }
        />
      </div>
    )
  }
)

SearchInput.displayName = 'SearchInput'
