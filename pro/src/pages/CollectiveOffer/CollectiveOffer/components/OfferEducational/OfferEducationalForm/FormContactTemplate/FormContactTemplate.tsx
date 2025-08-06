import { useFormContext } from 'react-hook-form'

import { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import { CheckboxGroup } from '@/ui-kit/form/CheckboxGroup/CheckboxGroup'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import styles from './FormContactTemplate.module.scss'
import { FormContactTemplateCustomForm } from './FormContactTemplateCustomForm/FormContactTemplateCustomForm'

interface FormContactTemplateProps {
  disableForm: boolean
}

export const FormContactTemplate = ({
  disableForm,
}: FormContactTemplateProps): JSX.Element => {
  const { watch, setValue, getFieldState, register, trigger } =
    useFormContext<OfferEducationalFormValues>()

  const contactOptions = [
    {
      label: 'Par email',
      checked: Boolean(watch('contactOptions')?.email),
      onChange: async (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue('contactOptions.email', e.target.checked)

        await trigger('contactOptions')
      },
      collapsed: (
        <div className={styles['contact-checkbox-inner-control']}>
          <TextInput
            label="Adresse email"
            {...register('email')}
            disabled={disableForm}
            description="Format : email@exemple.com"
            required
            error={getFieldState('email').error?.message}
          />
        </div>
      ),
    },
    {
      label: 'Par téléphone',
      checked: Boolean(watch('contactOptions')?.phone),
      onChange: async (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue('contactOptions.phone', e.target.checked)
        await trigger('contactOptions')
      },
      collapsed: (
        <div className={styles['contact-checkbox-inner-control']}>
          <PhoneNumberInput
            {...register('phone')}
            label="Numéro de téléphone"
            required
            disabled={disableForm}
            error={getFieldState('phone').error?.message}
          />
        </div>
      ),
    },
    {
      checked: Boolean(watch('contactOptions')?.form),
      onChange: async (e: React.ChangeEvent<HTMLInputElement>) => {
        setValue('contactOptions.form', e.target.checked)
        await trigger('contactOptions')
      },
      label: 'Via un formulaire',
      collapsed: <FormContactTemplateCustomForm disableForm={disableForm} />,
    },
  ]

  return (
    <div className={styles['container']}>
      <CheckboxGroup
        name="contactOptions"
        legend={
          <h2 className={styles['subtitle']}>
            Comment les enseignants peuvent-ils vous contacter ? *
          </h2>
        }
        required
        asterisk={false}
        group={contactOptions}
        disabled={disableForm}
        error={getFieldState('contactOptions').error?.message}
      />
    </div>
  )
}
