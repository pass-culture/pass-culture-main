import { FieldArray, FormikProvider, useFormik } from 'formik'
import React from 'react'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import fullNextIcon from 'icons/full-next.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeDateIcon from 'icons/stroke-date.svg'
import strokeEventsIcon from 'icons/stroke-events.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { isDateValid } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

import { getPriceCategoryOptions } from '../StocksEventEdition/getPriceCategoryOptions'

import { DayCheckbox } from './DayCheckbox'
import { computeInitialValues } from './form/computeInitialValues'
import { INITIAL_QUANTITY_PER_PRICE_CATEGORY } from './form/constants'
import { isLastWeekOfMonth } from './form/recurrenceUtils'
import {
  MonthlyOption,
  RecurrenceDays,
  RecurrenceFormValues,
  RecurrenceType,
} from './form/types'
import { getValidationSchema } from './form/validationSchema'
import styles from './RecurrenceForm.module.scss'

interface Props {
  setIsOpen: (p: boolean) => void
  priceCategories: PriceCategoryResponseModel[]
  handleSubmit: (values: RecurrenceFormValues) => Promise<void>
  idLabelledBy: string
}

const mapNumberToFrenchOrdinals = (n: number): string => {
  switch (n) {
    case 0:
      return 'premier'
    case 1:
      return 'deuxième'
    case 2:
      return 'troisième'
    case 3:
      return 'quatrième'
    case 4:
      return 'cinquième'
    default:
      throw new Error("A month couldn't have more than 5 weeks")
  }
}

const getMonthlyOptions = (values: RecurrenceFormValues) => {
  const startingDate = new Date(values.startingDate)
  const xOfMonth = isDateValid(startingDate) ? startingDate.getDate() : 1

  const weekOfMonth = isDateValid(startingDate)
    ? Math.floor((startingDate.getDate() - 1) / 7)
    : 0

  const isLastDayOfMonth = isLastWeekOfMonth(startingDate)

  const dayName = isDateValid(values.startingDate)
    ? formatLocalTimeDateString(
        new Date(values.startingDate),
        undefined,
        'eeeeeeee'
      ).replace('.', '')
    : ''

  const options = [
    {
      label: `Tous les ${xOfMonth} du mois`,
      value: MonthlyOption.X_OF_MONTH,
    },
    {
      label: `Le ${mapNumberToFrenchOrdinals(weekOfMonth)} ${dayName} du mois`,
      value: MonthlyOption.BY_FIRST_DAY,
    },
  ]
  if (isLastDayOfMonth) {
    options.push({
      label: `Le dernier ${dayName} du mois`,
      value: MonthlyOption.BY_LAST_DAY,
    })
  }

  return options
}

export const RecurrenceForm = ({
  setIsOpen,
  priceCategories,
  handleSubmit,
  idLabelledBy,
}: Props): JSX.Element => {
  const priceCategoryOptions = getPriceCategoryOptions(priceCategories)

  const formik = useFormik({
    initialValues: computeInitialValues(priceCategoryOptions),
    onSubmit: handleSubmit,
    validationSchema: getValidationSchema(priceCategoryOptions),
  })
  const { values, setFieldValue } = formik
  const monthlyOptions = getMonthlyOptions(values)

  const onRecurrenceTypeChange = async () => {
    await setFieldValue('startingDate', '')
    await setFieldValue('endingDate', '')
  }
  const minDateForEndingDate = isDateValid(values.startingDate)
    ? new Date(values.startingDate)
    : new Date()

  return (
    <FormikProvider value={formik}>
      <form onSubmit={formik.handleSubmit}>
        <h1 id={idLabelledBy} className={styles['title']}>
          Ajouter une ou plusieurs dates
        </h1>

        <div className={styles['mandatory']}>
          Tous les champs suivis d’un * sont obligatoires.
        </div>

        <fieldset>
          <div className={styles['section']}>
            <h2 className={styles['legend']}>
              <SvgIcon
                alt=""
                src={strokeDateIcon}
                className={styles['legend-icon']}
              />{' '}
              Cet évènement aura lieu
            </h2>

            <div className={styles['radio-group']}>
              <RadioButton
                label="Une seule fois"
                name="recurrenceType"
                value={RecurrenceType.UNIQUE}
                withBorder
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                label="Tous les jours"
                name="recurrenceType"
                value={RecurrenceType.DAILY}
                withBorder
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                label="Toutes les semaines"
                name="recurrenceType"
                value={RecurrenceType.WEEKLY}
                withBorder
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                label="Tous les mois"
                name="recurrenceType"
                value={RecurrenceType.MONTHLY}
                withBorder
                onChange={onRecurrenceTypeChange}
              />
            </div>

            {values.recurrenceType === RecurrenceType.WEEKLY && (
              <>
                <div className={styles['day-inputs']}>
                  <DayCheckbox
                    letter="L"
                    label="Lundi"
                    name="days"
                    value={RecurrenceDays.MONDAY}
                  />
                  <DayCheckbox
                    letter="M"
                    label="Mardi"
                    name="days"
                    value={RecurrenceDays.TUESDAY}
                  />
                  <DayCheckbox
                    letter="M"
                    label="Mercredi"
                    name="days"
                    value={RecurrenceDays.WEDNESDAY}
                  />
                  <DayCheckbox
                    letter="J"
                    label="Jeudi"
                    name="days"
                    value={RecurrenceDays.THURSDAY}
                  />
                  <DayCheckbox
                    letter="V"
                    label="Vendredi"
                    name="days"
                    value={RecurrenceDays.FRIDAY}
                  />
                  <DayCheckbox
                    letter="S"
                    label="Samedi"
                    name="days"
                    value={RecurrenceDays.SATURDAY}
                  />
                  <DayCheckbox
                    letter="D"
                    label="Dimanche"
                    name="days"
                    value={RecurrenceDays.SUNDAY}
                  />
                </div>
                {formik.errors.days && formik.touched.days && (
                  <div className={styles['days-error']}>
                    <FieldError name="days">{formik.errors.days}</FieldError>
                  </div>
                )}
              </>
            )}
            {values.recurrenceType !== RecurrenceType.MONTHLY && (
              <FormLayout.Row inline>
                <DatePicker
                  name="startingDate"
                  label={
                    values.recurrenceType === RecurrenceType.UNIQUE
                      ? 'Date de l’évènement'
                      : 'Du'
                  }
                  className={styles['date-input']}
                  minDate={new Date()}
                />

                {values.recurrenceType !== RecurrenceType.UNIQUE && (
                  <DatePicker
                    name="endingDate"
                    label="Au"
                    className={styles['date-input']}
                    minDate={minDateForEndingDate}
                  />
                )}
              </FormLayout.Row>
            )}

            {values.recurrenceType === RecurrenceType.MONTHLY && (
              <FormLayout.Row inline>
                <DatePicker
                  name="startingDate"
                  label={'Premier évènement le'}
                  className={styles['date-input']}
                  minDate={new Date()}
                />

                <Select
                  label="Détail de la récurrence"
                  name="monthlyOption"
                  options={monthlyOptions}
                  className={styles['monthly-option-input']}
                  defaultOption={{
                    label: 'Sélectionner une option',
                    value: '',
                  }}
                />

                <DatePicker
                  name="endingDate"
                  label="Fin de la récurrence"
                  className={styles['date-input']}
                  minDate={minDateForEndingDate}
                />
              </FormLayout.Row>
            )}
          </div>
        </fieldset>

        <fieldset>
          <div className={styles['section']}>
            <h2 className={styles['legend']}>
              <SvgIcon
                alt=""
                src={strokeClockIcon}
                className={styles['legend-icon']}
              />{' '}
              Horaires pour l’ensemble de ces dates
            </h2>

            <FormLayout.Row>
              <FieldArray
                name="beginningTimes"
                render={(arrayHelpers) => (
                  <>
                    <div className={styles['beginning-time-list']}>
                      {values.beginningTimes.map((beginningTime, index) => (
                        <TimePicker
                          key={index}
                          label={`Horaire ${index + 1}`}
                          name={`beginningTimes[${index}]`}
                          className={styles['beginning-time-input']}
                          clearButtonProps={{
                            tooltip: 'Supprimer',
                            'aria-label': 'Supprimer le créneau',
                            disabled: values.beginningTimes.length <= 1,
                            onClick: () => arrayHelpers.remove(index),
                          }}
                          hideFooter
                        />
                      ))}
                    </div>

                    <Button
                      variant={ButtonVariant.TERNARY}
                      icon={fullMoreIcon}
                      onClick={() => {
                        arrayHelpers.push('')
                        const inputToFocus = `beginningTimes[${values.beginningTimes.length}]`

                        // The input we want to focus has not been rendered yet
                        setTimeout(() => {
                          document.getElementById(inputToFocus)?.focus()
                        }, 0)
                      }}
                    >
                      Ajouter un créneau
                    </Button>
                  </>
                )}
              />
            </FormLayout.Row>
          </div>
        </fieldset>

        <fieldset>
          <div className={styles['section']}>
            <h2 className={styles['legend']}>
              <SvgIcon
                src={strokeEventsIcon}
                alt=""
                className={styles['legend-icon']}
              />
              Places et tarifs par horaire
            </h2>

            <FieldArray
              name="quantityPerPriceCategories"
              render={(arrayHelpers) => (
                <>
                  {values.quantityPerPriceCategories.map(
                    (quantityPerPriceCategory, index) => (
                      <FormLayout.Row key={index} inline mdSpaceAfter>
                        <TextInput
                          label="Nombre de places"
                          name={`quantityPerPriceCategories[${index}].quantity`}
                          type="number"
                          step="1"
                          isOptional
                          placeholder="Illimité"
                          className={styles['quantity-input']}
                          hideFooter
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
                          hideFooter
                        />

                        <div className={styles['align-icon']}>
                          <Button
                            variant={ButtonVariant.TERNARY}
                            icon={fullTrashIcon}
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
                  {values.quantityPerPriceCategories.length <
                    priceCategoryOptions.length && (
                    <ButtonLink
                      variant={ButtonVariant.TERNARY}
                      icon={fullMoreIcon}
                      onClick={() =>
                        arrayHelpers.push(INITIAL_QUANTITY_PER_PRICE_CATEGORY)
                      }
                      to={`#quantityPerPriceCategories[${
                        values.quantityPerPriceCategories.length - 1
                      }].quantity`}
                      isExternal
                    >
                      Ajouter d’autres places et tarifs
                    </ButtonLink>
                  )}
                </>
              )}
            />
          </div>
        </fieldset>

        <fieldset>
          <div className={styles['section']}>
            <h2 className={styles['legend']}>
              <SvgIcon
                alt=""
                src={strokeBookedIcon}
                className={styles['legend-icon']}
              />{' '}
              Date limite de réservation
            </h2>

            <div className={styles['booking-date-limit-container']}>
              <TextInput
                name="bookingLimitDateInterval"
                label="Date limite de réservation (en nombre de jours avant le début de l’évènement)"
                isLabelHidden
                type="number"
                step="1"
                className={styles['booking-date-limit-input']}
              />

              <div className={styles['booking-date-limit-text']}>
                jours avant le début de l’évènement
              </div>
            </div>
          </div>
        </fieldset>

        <div className={styles['action-buttons']}>
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={() => setIsOpen(false)}
          >
            Annuler
          </Button>

          <Button
            type="submit"
            icon={fullNextIcon}
            disabled={formik.isSubmitting}
            isLoading={formik.isSubmitting}
            iconPosition={IconPositionEnum.RIGHT}
          >
            Valider
          </Button>
        </div>
      </form>
    </FormikProvider>
  )
}
