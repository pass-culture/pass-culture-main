import { type ChangeEvent, useCallback, useMemo } from 'react'

import { Select, type SelectProps } from '@/ui-kit/form/Select/Select'

const EMPTY_OPTION_VALUE = '__EMPTY_OPTION__' as const

interface TypedSelectProps<Value extends number | string>
  extends Omit<SelectProps<Value>, 'onChange' | 'value'> {
  emptyOptionLabel?: string
  isNumber?: boolean
  onChange: (value: Value | undefined) => void
  value: Value | undefined
}
interface TypedNumberSelectProps extends TypedSelectProps<number> {
  isNumber: true
  onChange: (value: number | undefined) => void
}
interface TypedStringSelectProps extends TypedSelectProps<string> {
  isNumber?: false
  onChange: (value: string | undefined) => void
}

export function TypedSelect(props: TypedNumberSelectProps): JSX.Element
export function TypedSelect(props: TypedStringSelectProps): JSX.Element
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
      const normalizedNextValue =
        event.currentTarget.value === EMPTY_OPTION_VALUE
          ? undefined
          : isNumber
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
