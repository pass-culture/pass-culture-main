import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplateCustomForm.module.scss'

type FormContactTemplateCustomFormProps = {
  disableForm: boolean
}

export const FormContactTemplateCustomForm = ({
  disableForm,
}: FormContactTemplateCustomFormProps) => {
  return (
    <div className={styles['contact-checkbox-inner-control']}>
      <RadioGroup
        name="contactFormType"
        legend="Choisissez un type de formulaire"
        disabled={disableForm}
        variant={RadioVariant.BOX}
        group={[
          {
            label: 'le formulaire standard',
            value: 'form',
            childrenOnChecked: (
              <ButtonLink
                isExternal
                to="https://aide.passculture.app/hc/fr/articles/12957173606940--Acteurs-Culturels-Comment-paramétrer-les-options-de-contact-pour-les-enseignants-dans-le-cadre-d-une-offre-vitrine"
                opensInNewTab
                icon={fullLinkIcon}
                className={styles['custom-form-radio-link']}
              >
                FAQ : À quoi ressemble le formulaire standard ?
              </ButtonLink>
            ),
          },
          {
            label: 'mon propre formulaire',
            value: 'url',
            childrenOnChecked: (
              <TextInput
                label=""
                aria-label="URL de mon formulaire de contact"
                isOptional
                name="contactUrl"
                disabled={disableForm}
                description="Format : https://exemple.com"
                className={styles['custom-form-radio-input-control']}
              />
            ),
          },
        ]}
      />
    </div>
  )
}
