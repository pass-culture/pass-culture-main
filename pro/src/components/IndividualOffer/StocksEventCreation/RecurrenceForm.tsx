import * as Dialog from '@radix-ui/react-dialog'
import { FieldArray, FormikProvider, useFormik } from 'formik'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { isDateValid, mapDayToFrench } from 'commons/utils/date'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeDateIcon from 'icons/stroke-date.svg'
import strokeEventsIcon from 'icons/stroke-events.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { QuantityInput } from 'ui-kit/form/QuantityInput/QuantityInput'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { Select } from 'ui-kit/form/Select/Select'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { DayCheckbox } from 'ui-kit/formV2/DayCheckbox/DayCheckbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { getPriceCategoryOptions } from '../StocksEventEdition/getPriceCategoryOptions'

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

export interface RecurrenceFormProps {
  priceCategories: PriceCategoryResponseModel[]
  handleSubmit: (values: RecurrenceFormValues) => Promise<void>
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
  priceCategories,
  handleSubmit,
}: RecurrenceFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

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
      <form onSubmit={formik.handleSubmit} className={styles['form']}>
        <div className={styles['form-content']}>
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
                  variant={RadioVariant.BOX}
                  onChange={onRecurrenceTypeChange}
                />

                <RadioButton
                  label="Tous les jours"
                  name="recurrenceType"
                  value={RecurrenceType.DAILY}
                  variant={RadioVariant.BOX}
                  onChange={onRecurrenceTypeChange}
                />

                <RadioButton
                  label="Toutes les semaines"
                  name="recurrenceType"
                  value={RecurrenceType.WEEKLY}
                  variant={RadioVariant.BOX}
                  onChange={onRecurrenceTypeChange}
                />

                <RadioButton
                  label="Tous les mois"
                  name="recurrenceType"
                  value={RecurrenceType.MONTHLY}
                  variant={RadioVariant.BOX}
                  onChange={onRecurrenceTypeChange}
                />
              </div>

              {values.recurrenceType === RecurrenceType.WEEKLY && (
                <>
                  <div className={styles['day-inputs']}>
                    {Object.values(RecurrenceDays).map((day) => {
                      const frenchDay = mapDayToFrench(day)
                      return (
                        <DayCheckbox
                          key={day}
                          label={frenchDay[0]}
                          tooltipContent={frenchDay}
                          checked={values.days.includes(day)}
                          name="days"
                          onChange={(e) => {
                            let newDays = new Set(values.days)
                            if (e.target.checked) {
                              newDays.add(day)
                            } else {
                              newDays.delete(day)
                            }
                            // eslint-disable-next-line @typescript-eslint/no-floating-promises
                            setFieldValue('days', Array.from(newDays))
                          }}
                        />
                      )
                    })}
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
                        {values.beginningTimes.map((_beginningTime, index) => (
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
                    {values.quantityPerPriceCategories.map((_, index) => (
                      <FormLayout.Row
                        key={index}
                        inline
                        mdSpaceAfter
                        testId={`wrapper-quantityPerPriceCategories.${index}`}
                      >
                        <QuantityInput
                          label="Nombre de places"
                          name={`quantityPerPriceCategories[${index}].quantity`}
                          className={styles['quantity-input']}
                          isOptional
                          min={1}
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
                            icon={fullTrashIcon}
                            iconPosition={IconPositionEnum.CENTER}
                            disabled={
                              values.quantityPerPriceCategories.length <= 1
                            }
                            onClick={() => arrayHelpers.remove(index)}
                            tooltipContent="Supprimer les places"
                          />
                        </div>
                      </FormLayout.Row>
                    ))}
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
                  min={0}
                  className={styles['booking-date-limit-input']}
                  onBlur={() => {
                    if (
                      formik.initialValues.bookingLimitDateInterval !==
                      values.bookingLimitDateInterval
                    ) {
                      logEvent(Events.UPDATED_BOOKING_LIMIT_DATE, {
                        from: location.pathname,
                        bookingLimitDateInterval:
                          values.bookingLimitDateInterval,
                      })
                    }
                  }}
                />

                <div className={styles['booking-date-limit-text']}>
                  jours avant le début de l’évènement
                </div>
              </div>
            </div>
          </fieldset>
        </div>

        <DialogBuilder.Footer>
          <div className={styles['action-buttons']}>
            <Dialog.Close asChild>
              <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
            </Dialog.Close>

            <Button
              type="submit"
              disabled={formik.isSubmitting}
              isLoading={formik.isSubmitting}
            >
              Valider
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormikProvider>
  )
}
