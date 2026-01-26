import { useFormContext } from 'react-hook-form'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullLinkIcon from '@/icons/full-link.svg'

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
      <RadioButtonGroup
        name="contactFormType"
        label="Choisissez un type de formulaire"
        variant="detailed"
        disabled={disableForm}
        checkedOption={watch('contactFormType')}
        onChange={(e) => setValue('contactFormType', e.target.value)}
        options={[
          {
            label: 'Le formulaire standard',
            value: 'form',
            collapsed: (
              <div className={styles['custom-form-radio-link']}>
                <Button
                  as="a"
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  isExternal
                  to="https://aide.passculture.app/hc/fr/articles/12957173606940--Acteurs-Culturels-Comment-paramétrer-les-options-de-contact-pour-les-enseignants-dans-le-cadre-d-une-offre-vitrine"
                  opensInNewTab
                  icon={fullLinkIcon}
                  label="FAQ : À quoi ressemble le formulaire standard ?"
                />
              </div>
            ),
          },
          {
            label: 'Mon propre formulaire',
            value: 'url',
            collapsed: (
              <div className={styles['custom-form-radio-input-control']}>
                <TextInput
                  label="URL de mon formulaire de contact"
                  type="url"
                  required
                  {...register('contactUrl')}
                  error={getFieldState('contactUrl').error?.message}
                  disabled={disableForm}
                  description="Format : https://exemple.com"
                />
              </div>
            ),
          },
        ]}
      />
    </div>
  )
}
