import React from 'react'

import FormLayout from 'components/FormLayout'
import { MAX_DETAILS_LENGTH } from 'core/OfferEducational'
import { PRICE_INFORMATION } from 'screens/OfferEducational/constants/labels'
import { TextArea } from 'ui-kit'

import styles from '../OfferEducationalForm.module.scss'
interface FormPriceDetailsProps {
  disableForm: boolean
}

const FormPriceDetails = ({ disableForm }: FormPriceDetailsProps) => {
  return (
    <FormLayout.Section title="Prix">
      <FormLayout.Row>
        <TextArea
          className={styles['price-details']}
          countCharacters
          disabled={disableForm}
          isOptional
          label={PRICE_INFORMATION}
          maxLength={MAX_DETAILS_LENGTH}
          name="priceDetail"
          placeholder="Par exemple : tarif par élève ou par groupe scolaire, politique tarifaire REP/REP+ et accompagnateurs... "
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormPriceDetails
