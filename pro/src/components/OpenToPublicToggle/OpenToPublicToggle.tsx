import { useField } from 'formik'

import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'

import styles from './OpenToPublicToggle.module.scss'

export interface OpenToPublicToggleProps {
  radioDescriptions?: {
    yes?: string
    no?: string
  }
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

const DEFAULT_RADIO_DESCRIPTIONS: OpenToPublicToggleProps['radioDescriptions'] =
  {
    yes: 'Votre adresse postale sera visible.',
    no: 'Votre adresse postale ne sera pas visible.',
  }

export const OpenToPublicToggle = ({
  radioDescriptions = {},
  onChange,
}: OpenToPublicToggleProps): JSX.Element => {
  const [isOpenToPublic] = useField('isOpenToPublic')
  const finalRadioDescriptions = {
    ...DEFAULT_RADIO_DESCRIPTIONS,
    ...radioDescriptions,
  }

  return (
    <>
      <RadioGroup
        name="isOpenToPublic"
        className={styles['open-to-public-toggle']}
        legend="Accueillez-vous du public dans votre structure ?"
        describedBy="description"
        variant={RadioVariant.BOX}
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
        isOptional={false}
        onChange={onChange}
      />
      <span
        id="description"
        className={styles['open-to-public-toggle-description']}
        aria-live="polite"
      >
        {isOpenToPublic.value === 'true'
          ? finalRadioDescriptions.yes
          : isOpenToPublic.value === 'false'
            ? finalRadioDescriptions.no
            : ''}
      </span>
    </>
  )
}
