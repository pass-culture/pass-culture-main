import { FormLayout } from 'components/FormLayout/FormLayout'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { EMAIL_LABEL } from '../../constants/labels'

import styles from './FormContact.module.scss'

interface FormContactProps {
  disableForm: boolean
}

export const FormContact = ({ disableForm }: FormContactProps): JSX.Element => {
  return (
    <FormLayout.Section title="Comment les enseignants peuvent-ils vous contacter ?">
      <FormLayout.Row className={styles['phone-number-row']}>
        <PhoneNumberInput
          name="phone"
          label="Téléphone"
          disabled={disableForm}
          isOptional
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          label={EMAIL_LABEL}
          name="email"
          disabled={disableForm}
          description="Format : email@exemple.com"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
