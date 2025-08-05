import { FormLayout } from 'components/FormLayout/FormLayout'
import { useFormContext } from 'react-hook-form'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { EMAIL_LABEL } from '../../constants/labels'

import styles from './FormContact.module.scss'

interface FormContactProps {
  disableForm: boolean
}

export const FormContact = ({ disableForm }: FormContactProps): JSX.Element => {
  const { register, getFieldState } = useFormContext()

  return (
    <FormLayout.Section title="Comment les enseignants peuvent-ils vous contacter ?">
      <FormLayout.Row className={styles['phone-number-row']}>
        <PhoneNumberInput
          {...register('phone')}
          name="phone"
          label="Téléphone"
          disabled={disableForm}
          error={getFieldState('phone').error?.message}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label={EMAIL_LABEL}
          disabled={disableForm}
          description="Format : email@exemple.com"
          {...register('email')}
          required
          error={getFieldState('email').error?.message}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
