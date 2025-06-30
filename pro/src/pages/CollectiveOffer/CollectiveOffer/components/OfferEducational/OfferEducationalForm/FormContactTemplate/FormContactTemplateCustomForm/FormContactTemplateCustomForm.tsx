import { useFormContext } from 'react-hook-form'

import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplateCustomForm.module.scss'

type FormContactTemplateCustomFormProps = {
  disableForm: boolean
}

export const FormContactTemplateCustomForm = ({
  disableForm,
}: FormContactTemplateCustomFormProps) => {
  const { watch, setValue, register, getFieldState } = useFormContext()
  return (
    <div className={styles['contact-checkbox-inner-control']}>
      <RadioGroup
        name="contactFormType"
        legend="Choisissez un type de formulaire *"
        disabled={disableForm}
        checkedOption={watch('contactFormType')}
        onChange={(e) => setValue('contactFormType', e.target.value)}
        group={[
          {
            label: 'le formulaire standard',
            value: 'form',
            collapsed: (
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
            collapsed: (
              <TextInput
                label="URL de mon formulaire de contact"
                required
                {...register('contactUrl')}
                error={getFieldState('contactUrl').error?.message}
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
