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
                    if (inputRef.current) {
                      inputRef.current.value = ''
                      if (props.onChange) {
                        const event = {
                          currentTarget: inputRef.current,
                        } as React.ChangeEvent<HTMLInputElement>

                        props.onChange(event)
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
