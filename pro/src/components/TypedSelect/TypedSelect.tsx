import { type ChangeEvent, useCallback, useMemo } from 'react'

import { Select, type SelectProps } from '@/ui-kit/form/Select/Select'

import { EMPTY_OPTION_VALUE } from './constants'

interface TypedSelectProps<Value extends number | string>
  extends Omit<SelectProps<Value>, 'onChange' | 'value'> {
  emptyOptionLabel?: string
  isNumber?: boolean
  onChange: (value: Value | undefined) => void
  value: Value | undefined
}
interface TypedNumberSelectProps<Value extends number>
  extends TypedSelectProps<Value> {
  isNumber: true
  onChange: (value: Value | undefined) => void
}
interface TypedStringSelectProps<Value extends string>
  extends TypedSelectProps<Value> {
  isNumber?: false
  onChange: (value: Value | undefined) => void
}

export function TypedSelect<Value extends number>(
  props: TypedNumberSelectProps<Value>
): JSX.Element
export function TypedSelect<Value extends string>(
  props: TypedStringSelectProps<Value>
): JSX.Element
export function TypedSelect<Value extends number | string>({
  emptyOptionLabel,
  isNumber = false,
  options,
  value,
  onChange,
  ...rest
}: Readonly<TypedSelectProps<Value>>) {
  const denormalizedOptions = useMemo(
    () => [
      ...(emptyOptionLabel
        ? [{ label: emptyOptionLabel, value: EMPTY_OPTION_VALUE }]
        : []),
      ...options.map((option) => ({
        ...option,
        value: isNumber ? Number(option.value) : option.value,
      })),
    ],
    [emptyOptionLabel, isNumber, options]
  )
  const denormalizedValue =
    value === null || value === undefined ? EMPTY_OPTION_VALUE : String(value)

  const handleChange = useCallback(
    (event: ChangeEvent<HTMLSelectElement>) => {
      if (event.currentTarget.value === EMPTY_OPTION_VALUE) {
        onChange(undefined)

        return
      }

      const normalizedNextValue = isNumber
        ? Number(event.currentTarget.value)
        : event.currentTarget.value

      onChange(normalizedNextValue as Parameters<typeof onChange>[0])
    },
    [isNumber, onChange]
  )

  return (
    <Select
      {...rest}
      options={denormalizedOptions}
      onChange={handleChange}
      value={denormalizedValue}
    />
  )
}
