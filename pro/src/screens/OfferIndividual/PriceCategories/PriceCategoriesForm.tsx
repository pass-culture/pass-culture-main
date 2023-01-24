import cn from 'classnames'
import { FieldArray, useFormikContext } from 'formik'
import React, { useState } from 'react'

import FormLayout from 'components/FormLayout'
import { IcoEuro, IconPlusCircle } from 'icons'
import { Button, TextInput, Checkbox, InfoBox } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseCheckbox } from 'ui-kit/form/shared'

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

const setFreeCheckboxValue = (
  array: boolean[],
  index: number,
  value: boolean
): boolean[] => {
  return array.map((isSelected, i) => {
    if (i === index) {
      return value
    } else {
      return isSelected
    }
  })
}

export const PriceCategoriesForm = ({
  values,
}: PriceCategoriesFormProps): JSX.Element => {
  const { setFieldValue, handleChange } = useFormikContext()

  const [isSelectedArray, setIsSelectedArray] = useState(
    // initialize an array of lenght with false or true when it's 0
    Array.from(
      Array(PRICE_CATEGORY_MAX_LENGTH),
      (_, index) => values.priceCategories.at(index)?.price === 0
    )
  )

  const onChangeFree =
    (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
      /* istanbul ignore next: tested but coverage don't see it */
      if (e.target.checked) {
        setFieldValue(`priceCategories[${index}].price`, 0)
      }
      setIsSelectedArray(
        setFreeCheckboxValue(isSelectedArray, index, e.target.checked)
      )
    }

  const onChangePrice =
    (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
      /* istanbul ignore next: tested but coverage don't see it */
      if (e.target.value !== '0') {
        setIsSelectedArray(setFreeCheckboxValue(isSelectedArray, index, false))
        /* istanbul ignore next: tested but coverage don't see it */
      } else {
        setIsSelectedArray(setFreeCheckboxValue(isSelectedArray, index, true))
      }
      handleChange(e)
    }

  return (
    <>
      <FormLayout.MandatoryInfo />
      <FieldArray
        name="priceCategories"
        render={arrayHelpers => (
          <FormLayout.Section title="Tarifs">
            {values.priceCategories.map((priceCategory, index) => (
              <FormLayout.Row key={index} inline>
                <TextInput
                  smallLabel
                  name={`priceCategories[${index}].label`}
                  label="Intitulé du tarif"
                  placeholder="Ex : catégorie 1, orchestre..."
                  maxLength={PRICE_CATEGORY_LABEL_MAX_LENGTH}
                  countCharacters
                  className={cn(
                    styles['label-input'],
                    styles['field-layout-align-self']
                  )}
                  isLabelHidden={index !== 0}
                />
                <TextInput
                  smallLabel
                  name={`priceCategories[${index}].price`}
                  label="Tarif par personne"
                  placeholder="Ex : 25€"
                  type="number"
                  step="0.01"
                  max={PRICE_CATEGORY_PRICE_MAX}
                  rightIcon={() => <IcoEuro />}
                  className={cn(
                    styles['price-input'],
                    styles['field-layout-align-self']
                  )}
                  onChange={onChangePrice(index)}
                  isLabelHidden={index !== 0}
                />
                <BaseCheckbox
                  label="Gratuit"
                  checked={isSelectedArray[index]}
                  name={`priceCategories[${index}].free`}
                  onChange={onChangeFree(index)}
                  className={cn(
                    {
                      [styles['first-free-input']]: index === 0,
                      [styles['other-free-input']]: index !== 0,
                    },
                    styles['field-layout-align-self']
                  )}
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
