import { useState } from 'react'
import type { UseFormRegisterReturn } from 'react-hook-form'

import type { AdresseData } from '@/apiClient/adresse/types'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { AddressSelect } from '@/ui-kit/form/AddressSelect/AddressSelect'

type AddressFieldProps = {
  addressRegister: UseFormRegisterReturn
  label?: string
  description?: string
  error?: string
  disabled?: boolean
  className?: string

  onAddressChosen: (address: AdresseData) => void

  manual?: boolean
  onManualChange?: (next: boolean) => void

  renderManual?: () => React.ReactNode
}

export function AddressField({
  addressRegister,
  label = 'Adresse postale',
  description,
  error,
  disabled = false,
  className,
  onAddressChosen,
  manual,
  onManualChange,
  renderManual,
}: AddressFieldProps) {
  const [internalManual, setInternalManual] = useState(false)
  const isManual = manual ?? internalManual

  const setManual = (next: boolean) => {
    onManualChange?.(next)
    if (manual === undefined) {
      setInternalManual(next)
    }
  }

  return (
    <>
      <AddressSelect
        {...addressRegister}
        className={className}
        disabled={disabled || isManual}
        error={!disabled && !isManual ? error : undefined}
        label={label}
        description={description}
        onAddressChosen={onAddressChosen}
      />

      <Button
        type="button"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={isManual ? fullBackIcon : fullNextIcon}
        onClick={() => setManual(!isManual)}
        disabled={disabled}
        label={
          isManual
            ? 'Revenir à la sélection automatique'
            : 'Vous ne trouvez pas votre adresse ?'
        }
      />

      {isManual && renderManual?.()}
    </>
  )
}
