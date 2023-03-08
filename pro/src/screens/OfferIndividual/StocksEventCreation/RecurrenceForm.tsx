import { FieldArray, FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { IStocksEvent } from 'components/StocksEventList/StocksEventList'
import { IOfferIndividual } from 'core/Offers/types'
import {
  CalendarCheckIcon,
  CircleArrowIcon,
  ClockIcon,
  DateIcon,
  EventsIcon,
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
        <FormLayout.Section title="Ajouter une ou plusieurs dates">
          <div className={styles['section']}>
            <div className={styles['legend']}>
              <DateIcon className={styles['legend-icon']} /> Cet évènement aura
              lieu
            </div>

            <div className={styles['radio-group']}>
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

              <RadioButton
                variant={BaseRadioVariant.SECONDARY}
                label="Toutes les semaines"
                name="recurrenceType"
                value={RecurrenceType.WEEKLY}
                withBorder
                disabled
              />

              <RadioButton
                variant={BaseRadioVariant.SECONDARY}
                label="Tous les mois"
                name="recurrenceType"
                value={RecurrenceType.MONTHLY}
                withBorder
                disabled
              />
            </div>

            <FormLayout.Row inline>
              <DatePicker
                name="startingDate"
                label={
                  values.recurrenceType === RecurrenceType.UNIQUE
                    ? 'Date de l’évènement'
                    : 'Du'
                }
                className={styles['date-input']}
              />

              {values.recurrenceType !== RecurrenceType.UNIQUE && (
                <DatePicker
                  name="endingDate"
                  label="Au"
                  className={styles['date-input']}
                />
              )}
            </FormLayout.Row>
          </div>

          <div className={styles['section']}>
            <div className={styles['legend']}>
              <ClockIcon className={styles['legend-icon']} /> Horaires pour
              l’ensemble de ces dates
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
          </div>

          <div className={styles['section']}>
            <div className={styles['legend']}>
              <EventsIcon className={styles['legend-icon']} /> Places et tarifs
              par horaire
            </div>

            <FieldArray
              name="quantityPerPriceCategories"
              render={arrayHelpers => (
                <>
                  {values.quantityPerPriceCategories.map(
                    (quantityPerPriceCategory, index) => (
                      <FormLayout.Row key={index} inline smSpaceAfter>
                        <TextInput
                          label="Nombre de places"
                          name={`quantityPerPriceCategories[${index}].quantity`}
                          type="number"
                          step="1"
                          placeholder="Illimité"
                          className={styles['quantity-input']}
                        />

                        <Select
                          label="Tarif"
                          name={`quantityPerPriceCategories[${index}].priceCategory`}
                          options={priceCategoryOptions}
                          defaultOption={{
                            label: 'Sélectionner un tarif',
                            value: '',
                          }}
                          className={styles['price-category-input']}
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
          </div>

          <div className={styles['section']}>
            <div className={styles['legend']}>
              <CalendarCheckIcon className={styles['legend-icon']} /> Date
              limite de réservation
            </div>

            <div className={styles['booking-date-limit-container']}>
              <TextInput
                name="bookingLimitDateInterval"
                label="Nombre de jours avant le début de l’évènement"
                isLabelHidden
                type="number"
                step="1"
                className={styles['booking-date-limit-input']}
              />

              <div>jours avant le début de l’évènement</div>
            </div>
          </div>
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
