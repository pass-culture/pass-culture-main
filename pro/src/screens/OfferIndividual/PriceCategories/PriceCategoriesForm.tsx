import { FieldArray } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IcoEuro } from 'icons'
import { TextInput } from 'ui-kit'

import {
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_PRICE_MAX,
} from './form/constants'
import { PriceCategoriesFormValues } from './form/types'
import styles from './PriceCategoriesForm.module.scss'

type PriceCategoriesFormProps = {
  values: PriceCategoriesFormValues
}

export const PriceCategoriesForm = ({
  values,
}: PriceCategoriesFormProps): JSX.Element => {
  return (
    <FieldArray
      name="priceCategories"
      render={() => (
        <FormLayout.Section title="Tarifs">
          {values.priceCategories.map((priceCategory, index) => (
            <FormLayout.Row key={index} inline>
              <TextInput
                name={`priceCategories[${index}].label`}
                label="Intitulé du tarif"
                placeholder="Ex : catégorie 1, orchestre..."
                maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                countCharacters
                className={styles['label-input']}
              />
              <TextInput
                name={`priceCategories[${index}].price`}
                label="Tarif par personne"
                placeholder="Ex : 25€"
                type="number"
                step="0.01"
                max={PRICE_CATEGORY_PRICE_MAX}
                rightIcon={() => <IcoEuro />}
                className={styles['price-input']}
              />
            </FormLayout.Row>
          ))}
        </FormLayout.Section>
      )}
    />
  )
}
