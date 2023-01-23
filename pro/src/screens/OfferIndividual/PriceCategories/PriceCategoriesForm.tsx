import { FieldArray } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IcoEuro, IconPlusCircle } from 'icons'
import { Button, TextInput, Checkbox, InfoBox } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_LABEL_MAX_LENGTH,
  PRICE_CATEGORY_MAX_LENGTH,
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
    <>
      <FieldArray
        name="priceCategories"
        render={arrayHelpers => (
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
            <Button
              variant={ButtonVariant.TERNARY}
              Icon={IconPlusCircle}
              onClick={() => arrayHelpers.push(INITIAL_PRICE_CATEGORY)}
              disabled={
                values.priceCategories.length >= PRICE_CATEGORY_MAX_LENGTH
              }
            >
              Ajouter un tarif
            </Button>
          </FormLayout.Section>
        )}
      />
      <FormLayout.Section
        className={styles['duo-section']}
        title="Réservations “Duo”"
      >
        <FormLayout.Row
          sideComponent={
            <InfoBox
              type="info"
              text="Cette option permet au bénéficiaire de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l'accompagnateur."
            />
          }
        >
          <Checkbox
            label="Accepter les réservations “Duo“"
            name="isDuo"
            withBorder
          />
        </FormLayout.Row>
      </FormLayout.Section>
    </>
  )
}
