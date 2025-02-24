import { useField } from "formik"

import { RadioGroup } from "ui-kit/form/RadioGroup/RadioGroup"
import { RadioVariant } from "ui-kit/form/shared/BaseRadio/BaseRadio"

import styles from "./OpenToPublicToggle.module.scss"

export const OpenToPublicToggle = (): JSX.Element => {
  const [isOpenToPublic] = useField('isOpenToPublic')

  return (
    <>
      <RadioGroup
        name="isOpenToPublic"
        className={styles['open-to-public-toggle']}
        childrenClassName={styles['open-to-public-toggle-children']}
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
        isOptional={false}
      />
      <span
        id="description"
        className={styles ['open-to-public-toggle-description']}
        aria-live="polite"
      >
        {isOpenToPublic.value === 'true'
          ? 'Votre adresse postale sera visible'
          : isOpenToPublic.value === 'false'
          ? 'Votre adresse postale ne sera pas visible'
          : ''
        }
      </span>
    </>
  )
}