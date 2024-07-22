import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { FieldSetLayout } from 'ui-kit/form/shared/FieldSetLayout/FieldSetLayout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplateCustomForm.module.scss'

type FormContactTemplateCustomFormProps = {
  disableForm: boolean
}

export const FormContactTemplateCustomForm = ({
  disableForm,
}: FormContactTemplateCustomFormProps) => {
  return (
    <FieldSetLayout
      name="contactForm"
      className={styles['custom-form']}
      hideFooter
    >
      <div className={styles['custom-form-radio']}>
        <RadioButton
          label="le formulaire standard"
          name="contactFormType"
          disabled={disableForm}
          value="form"
        />
        <ButtonLink
          isExternal
          to="https://aide.passculture.app/hc/fr/articles/12957173606940--Acteurs-Culturels-Comment-paramétrer-les-options-de-contact-pour-les-enseignants-dans-le-cadre-d-une-offre-vitrine"
          opensInNewTab
          icon={fullLinkIcon}
          className={styles['custom-form-radio-link']}
        >
          FAQ : À quoi ressemble le formulaire standard ?
        </ButtonLink>
      </div>
      <div className={styles['custom-form-radio']}>
        <RadioButton
          label="mon propre formulaire accessible à cette URL"
          name="contactFormType"
          disabled={disableForm}
          value="url"
        />
        <TextInput
          label=""
          aria-label="URL de mon formulaire de contact"
          isOptional
          name="contactUrl"
          disabled={disableForm}
          placeholder="https://exemple.com"
          className={styles['custom-form-radio-input-control']}
        />
      </div>
    </FieldSetLayout>
  )
}
