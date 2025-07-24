import { useId, useState } from 'react'

import { Checkbox, CheckboxProps } from '../Checkbox/Checkbox'

// Types exclusifs pour la gestion des assets selon la variante

type CheckboxGroupOptionSimple = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant' | 'asset'
> & {
  label: string
  value: string | number
  variant?: 'default'
  asset?: never
}

type CheckboxGroupOptionDetailed = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant'
> & {
  label: string
  value: string | number
  variant: 'detailed'
  asset?: CheckboxProps['asset']
}

export type CheckboxGroupOption =
  | CheckboxGroupOptionSimple
  | CheckboxGroupOptionDetailed

type CheckboxGroupProps = {
  label: string
  description?: string
  error?: string
  options: CheckboxGroupOption[]
  value?: (string | number)[]
  defaultValue?: (string | number)[]
  onChange?: (value: (string | number)[]) => void
  display?: 'vertical' | 'horizontal'
  variant?: 'default' | 'detailed'
  disabled?: boolean
}

export const CheckboxGroup = ({
  label,
  description,
  error,
  options,
  value,
  defaultValue,
  onChange,
  variant = 'default',
  disabled = false,
}: CheckboxGroupProps) => {
  // Sécurité : au moins 2 options
  if (options.length < 2) {
    throw new Error('CheckboxGroup requires at least two options.')
  }

  // Génération des ids pour l'accessibilité
  const labelId = useId()
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = [
    error ? errorId : null,
    description ? descriptionId : null,
  ]
    .filter(Boolean)
    .join(' ')

  // Contrôlé / non-contrôlé
  const isControlled = value !== undefined
  const [internalValue, setInternalValue] = useState<(string | number)[]>(
    defaultValue ?? []
  )
  const selectedValues = isControlled ? value! : internalValue

  // Gestion du changement de sélection
  const handleChange = (optionValue: string | number) => {
    let newValues: (string | number)[]
    if (selectedValues.includes(optionValue)) {
      newValues = selectedValues.filter((v) => v !== optionValue)
    } else {
      newValues = [...selectedValues, optionValue]
    }
    if (!isControlled) {
      setInternalValue(newValues)
    }
    onChange?.(newValues)
  }

  // Gestion de la propagation des props asset/variant
  const propagateAsset =
    variant === 'detailed' && options.some((opt) => 'asset' in opt && opt.asset)

  return (
    <div
      role="group"
      aria-labelledby={labelId}
      aria-describedby={describedBy || undefined}
    >
      <div>
        <span id={labelId}>{label}</span>
        {description && <span id={descriptionId}>{description}</span>}
        <div role="alert" id={errorId}>
          {error && <span>{error}</span>}
        </div>
      </div>
      <div>
        {options.map((option) => {
          const checked = selectedValues.includes(option.value)

          const detailedProps: Record<string, any> =
            option.variant === 'detailed'
              ? {
                  description: option.description,
                  asset: propagateAsset ? option.asset : undefined,
                  collapsed: option.collapsed,
                }
              : {}

          return (
            <Checkbox
              key={option.value}
              label={option.label}
              checked={checked}
              onChange={() => handleChange(option.value)}
              hasError={!!error}
              disabled={disabled}
              sizing={option.sizing}
              indeterminate={option.indeterminate}
              name={option.name}
              required={option.required}
              asterisk={option.asterisk}
              onBlur={option.onBlur}
              variant={option.variant}
              {...detailedProps}
            />
          )
        })}
      </div>
    </div>
  )
}
