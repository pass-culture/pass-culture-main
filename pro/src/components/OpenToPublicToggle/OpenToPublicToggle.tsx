import cn from 'classnames'
import { useId } from 'react'

import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'

import styles from './OpenToPublicToggle.module.scss'

export interface OpenToPublicToggleProps {
  className?: string
  radioDescriptions?: {
    yes?: string
    no?: string
  }
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  isOpenToPublic?: string | null
}

const DEFAULT_RADIO_DESCRIPTIONS: OpenToPublicToggleProps['radioDescriptions'] =
  {
    yes: 'Votre adresse postale sera visible.',
    no: 'Votre adresse postale ne sera pas visible.',
  }

export const OpenToPublicToggle = ({
  className,
  radioDescriptions = {},
  onChange,
  isOpenToPublic,
}: OpenToPublicToggleProps): JSX.Element => {
  const descriptionId = useId()

  const finalRadioDescriptions = {
    ...DEFAULT_RADIO_DESCRIPTIONS,
    ...radioDescriptions,
  }

  return (
    <>
      <RadioGroup
        name="isOpenToPublic"
        className={cn(styles['open-to-public-toggle'], className)}
        legend="Accueillez-vous du public dans votre structure ?"
        describedBy={descriptionId}
        variant="detailed"
        group={[
          {
            label: 'Oui',
            value: 'true',
          },
          {
            label: 'Non',
            value: 'false',
          },
        ]}
        displayMode="inline"
        onChange={onChange}
        checkedOption={isOpenToPublic?.toString()}
      />
      <span
        id={descriptionId}
        className={styles['open-to-public-toggle-description']}
        aria-live="polite"
      >
        {isOpenToPublic === 'true'
          ? finalRadioDescriptions.yes
          : isOpenToPublic === 'false'
            ? finalRadioDescriptions.no
            : ''}
      </span>
    </>
  )
}
