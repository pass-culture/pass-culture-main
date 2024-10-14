import React from 'react'

import { MAX_DETAILS_LENGTH } from 'commons/core/OfferEducational/constants'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'

import { PRICE_INFORMATION } from '../../constants/labels'
import styles from '../OfferEducationalForm.module.scss'

interface FormPriceDetailsProps {
  disableForm: boolean
}

export const FormPriceDetails = ({ disableForm }: FormPriceDetailsProps) => {
  return (
    <FormLayout.Section title="Prix">
      <FormLayout.Row>
        <TextArea
          className={styles['price-details']}
          disabled={disableForm}
          isOptional
          label={PRICE_INFORMATION}
          maxLength={MAX_DETAILS_LENGTH}
          name="priceDetail"
          description="Par exemple : tarif par élève ou par groupe scolaire, politique tarifaire REP/REP+ et accompagnateurs... "
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
