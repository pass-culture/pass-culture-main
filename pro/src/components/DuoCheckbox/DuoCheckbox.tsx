import { forwardRef } from 'react'

import { Checkbox, CheckboxProps } from 'design-system/Checkbox/Checkbox'
import strokeDuoIcon from 'icons/stroke-duo.svg'

export const DuoCheckbox = forwardRef<
  HTMLInputElement,
  Omit<CheckboxProps, 'label' | 'variant' | 'description' | 'asset'>
>((props, ref) => {
  return (
    <Checkbox
      description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
      label="Accepter les réservations “Duo“"
      variant="detailed"
      sizing="fill"
      asset={{
        variant: 'icon',
        src: strokeDuoIcon,
      }}
      {...props}
      ref={ref}
    />
  )
})

DuoCheckbox.displayName = 'DuoCheckbox'
