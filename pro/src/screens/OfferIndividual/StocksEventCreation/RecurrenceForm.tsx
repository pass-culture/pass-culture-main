import { FieldArray, FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IStocksEvent } from 'components/StocksEventList/StocksEventList'
import { IOfferIndividual } from 'core/Offers/types'
import {
  CalendarIcon,
  CircleArrowIcon,
  PlusCircleIcon,
  TrashFilledIcon,
} from 'icons'
import {
  Button,
  DatePicker,
  RadioButton,
  Select,
  SubmitButton,
  TextInput,
  TimePicker,
} from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'

import { getPriceCategoryOptions } from '../StocksEventEdition/StocksEventEdition'

import { computeInitialValues } from './form/computeInitialValues'
import { INITIAL_QUANTITY_PER_PRICE_CATEGORY } from './form/constants'
import { onSubmit } from './form/onSubmit'
import { RecurrenceFormValues, RecurrenceType } from './form/types'
import { getValidationSchema } from './form/validationSchema'
import styles from './RecurrenceForm.module.scss'

interface Props {
  offer: IOfferIndividual
  onCancel: () => void
  onConfirm: (newStocks: IStocksEvent[]) => void
}

export const RecurrenceForm = ({
  offer,
  onCancel,
  onConfirm,
}: Props): JSX.Element => {
  const priceCategoryOptions = getPriceCategoryOptions(offer)
  const handleSubmit = (values: RecurrenceFormValues) => {
    const newStocks = onSubmit(values, offer.venue.departmentCode)
    onConfirm(newStocks)
  }

  const formik = useFormik({
    initialValues: computeInitialValues(priceCategoryOptions),
    onSubmit: handleSubmit,
    validationSchema: getValidationSchema(priceCategoryOptions),
  })
  const { values } = formik

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <FormLayout.Section title="Ajouter une récurrence">
          <div className={styles['legend']}>
            <CalendarIcon className={styles['legend-icon']} /> Cet évènement
            aura lieu
          </div>

          <FormLayout.Row inline>
            <RadioButton
              variant={BaseRadioVariant.SECONDARY}
              label="Une seule fois"
              name="recurrenceType"
              value={RecurrenceType.UNIQUE}
              withBorder
            />

            <RadioButton
              variant={BaseRadioVariant.SECONDARY}
              label="Tous les jours"
              name="recurrenceType"
              value={RecurrenceType.DAILY}
              withBorder
            />
          </FormLayout.Row>

          <FormLayout.Row inline>
            <DatePicker
              name="startingDate"
              label={
                values.recurrenceType === RecurrenceType.UNIQUE
                  ? 'Date de l’évènement'
                  : 'Du'
              }
            />

            {values.recurrenceType !== RecurrenceType.UNIQUE && (
              <DatePicker name="endingDate" label="Au" />
            )}
          </FormLayout.Row>

          <div className={styles['legend']}>
            <CalendarIcon className={styles['legend-icon']} /> Créneaux horaires
            (pour l’ensemble de ces dates)
          </div>

          <FormLayout.Row>
            <FieldArray
              name="beginningTimes"
              render={arrayHelpers => (
                <>
                  <div className={styles['beginning-time-list']}>
                    {values.beginningTimes.map((beginningTime, index) => (
                      <div
                        key={index}
                        className={styles['beginning-time-wrapper']}
                      >
                        <TimePicker
                          label={`Horaire ${index + 1}`}
                          name={`beginningTimes[${index}]`}
                        />

                        <div className={styles['align-icon']}>
                          <Button
                            variant={ButtonVariant.TERNARY}
                            Icon={TrashFilledIcon}
                            iconPosition={IconPositionEnum.CENTER}
                            disabled={values.beginningTimes.length <= 1}
                            onClick={() => arrayHelpers.remove(index)}
                            hasTooltip
                          >
                            Supprimer le créneau
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Button
                    variant={ButtonVariant.TERNARY}
                    Icon={PlusCircleIcon}
                    onClick={() => arrayHelpers.push('')}
                  >
                    Ajouter un créneau
                  </Button>
                </>
              )}
            />
          </FormLayout.Row>

          <div className={styles['legend']}>
            <CalendarIcon className={styles['legend-icon']} /> Places et tarifs
          </div>

          <FieldArray
            name="quantityPerPriceCategories"
            render={arrayHelpers => (
              <>
                {values.quantityPerPriceCategories.map(
                  (quantityPerPriceCategory, index) => (
                    <FormLayout.Row key={index} inline>
                      <TextInput
                        label="Nombre de places"
                        name={`quantityPerPriceCategories[${index}].quantity`}
                        type="number"
                        step="1"
                        placeholder="Illimité"
                      />

                      <Select
                        label="Tarif"
                        name={`quantityPerPriceCategories[${index}].priceCategory`}
                        options={priceCategoryOptions}
                        defaultOption={{
                          label: 'Sélectionner un tarif',
                          value: '',
                        }}
                      />

                      <div className={styles['align-icon']}>
                        <Button
                          variant={ButtonVariant.TERNARY}
                          Icon={TrashFilledIcon}
                          iconPosition={IconPositionEnum.CENTER}
                          disabled={
                            values.quantityPerPriceCategories.length <= 1
                          }
                          onClick={() => arrayHelpers.remove(index)}
                          hasTooltip
                        >
                          Supprimer les places
                        </Button>
                      </div>
                    </FormLayout.Row>
                  )
                )}

                <Button
                  variant={ButtonVariant.TERNARY}
                  Icon={PlusCircleIcon}
                  onClick={() =>
                    arrayHelpers.push(INITIAL_QUANTITY_PER_PRICE_CATEGORY)
                  }
                >
                  Ajouter d’autres places et tarifs
                </Button>
              </>
            )}
          />

          <FormLayout.Row inline>
            <TextInput
              label="Date limite de réservation"
              name="bookingLimitDateInterval"
              type="number"
              step="1"
            />
            <div>jours avant le début de l’évènement</div>
          </FormLayout.Row>
        </FormLayout.Section>

        <div className={styles['action-buttons']}>
          <Button variant={ButtonVariant.SECONDARY} onClick={onCancel}>
            Annuler
          </Button>

          <SubmitButton
            Icon={CircleArrowIcon}
            iconPosition={IconPositionEnum.RIGHT}
          >
            Ajouter cette date
          </SubmitButton>
        </div>
      </form>
    </FormikProvider>
  )
}
