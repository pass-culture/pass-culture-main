import { FieldArray, FormikProvider, useFormik } from 'formik'
import React from 'react'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
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
  ButtonLink,
  DatePicker,
  RadioButton,
  Select,
  SubmitButton,
  TextInput,
  TimePicker,
} from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { FieldError } from 'ui-kit/form/shared'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import { formatLocalTimeDateString } from 'utils/timezone'

import { getPriceCategoryOptions } from '../StocksEventEdition/StocksEventEdition'

import { DayCheckbox } from './DayCheckbox'
import { computeInitialValues } from './form/computeInitialValues'
import { INITIAL_QUANTITY_PER_PRICE_CATEGORY } from './form/constants'
import { onSubmit } from './form/onSubmit'
import { isLastWeekOfMonth } from './form/recurrenceUtils'
import {
  RecurrenceDays,
  RecurrenceType,
  RecurrenceFormValues,
  MonthlyOption,
} from './form/types'
import { getValidationSchema } from './form/validationSchema'
import styles from './RecurrenceForm.module.scss'

interface Props {
  offer: IOfferIndividual
  onCancel: () => void
  onConfirm: (newStocks: StocksEvent[]) => void
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
  const xOfMonth = values.startingDate ? values.startingDate.getDate() : 1

  const weekOfMonth = values.startingDate
    ? Math.floor((values.startingDate.getDate() - 1) / 7)
    : 0

  const lastDayofMonth = isLastWeekOfMonth(values.startingDate)

  const dayName = values.startingDate
    ? formatLocalTimeDateString(
        values.startingDate,
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
  if (lastDayofMonth) {
    options.push({
      label: `Le dernier ${dayName} du mois`,
      value: MonthlyOption.BY_LAST_DAY,
    })
  }

  return options
}

export const RecurrenceForm = ({
  offer,
  onCancel,
  onConfirm,
}: Props): JSX.Element => {
  const { logEvent } = useAnalytics()
  const priceCategoryOptions = getPriceCategoryOptions(offer.priceCategories)
  const mode = useOfferWizardMode()

  const handleSubmit = (values: RecurrenceFormValues) => {
    const newStocks = onSubmit(values, offer.venue.departmentCode)
    onConfirm(newStocks)
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.STOCKS,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.RECURRENCE_POPIN,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offer.nonHumanizedId,
      recurrenceType: values.recurrenceType,
    })
  }

  const formik = useFormik({
    initialValues: computeInitialValues(priceCategoryOptions),
    onSubmit: handleSubmit,
    validationSchema: getValidationSchema(priceCategoryOptions),
  })
  const { values, setFieldValue } = formik
  const monthlyOptions = getMonthlyOptions(values)

  const onRecurrenceTypeChange = () => {
    setFieldValue('startingDate', '')
    setFieldValue('endingDate', '')
  }

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
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                variant={BaseRadioVariant.SECONDARY}
                label="Tous les jours"
                name="recurrenceType"
                value={RecurrenceType.DAILY}
                withBorder
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                variant={BaseRadioVariant.SECONDARY}
                label="Toutes les semaines"
                name="recurrenceType"
                value={RecurrenceType.WEEKLY}
                withBorder
                onChange={onRecurrenceTypeChange}
              />

              <RadioButton
                variant={BaseRadioVariant.SECONDARY}
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
                  minDateTime={new Date()}
                />

                {values.recurrenceType !== RecurrenceType.UNIQUE && (
                  <DatePicker
                    name="endingDate"
                    label="Au"
                    className={styles['date-input']}
                    minDateTime={new Date()}
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
                  minDateTime={new Date()}
                />

                <Select
                  label="Détail de la récurrence"
                  name="monthlyOption"
                  options={monthlyOptions}
                  className={styles['price-category-input']}
                  defaultOption={{
                    label: 'Sélectionner une option',
                    value: '',
                  }}
                />

                <DatePicker
                  name="endingDate"
                  label="Fin de la récurrence"
                  className={styles['date-input']}
                  minDateTime={new Date()}
                />
              </FormLayout.Row>
            )}
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

                    <ButtonLink
                      variant={ButtonVariant.TERNARY}
                      Icon={PlusCircleIcon}
                      onClick={() => arrayHelpers.push('')}
                      link={{
                        to: `#beginningTimes[${
                          values.beginningTimes.length - 1
                        }]`,
                        isExternal: true,
                      }}
                    >
                      Ajouter un créneau
                    </ButtonLink>
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
                      <FormLayout.Row key={index} inline mdSpaceAfter>
                        <TextInput
                          label="Nombre de places"
                          name={`quantityPerPriceCategories[${index}].quantity`}
                          type="number"
                          step="1"
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
                  {values.quantityPerPriceCategories.length <
                    priceCategoryOptions.length && (
                    <ButtonLink
                      variant={ButtonVariant.TERNARY}
                      Icon={PlusCircleIcon}
                      onClick={() =>
                        arrayHelpers.push(INITIAL_QUANTITY_PER_PRICE_CATEGORY)
                      }
                      link={{
                        to: `#quantityPerPriceCategories[${
                          values.quantityPerPriceCategories.length - 1
                        }].quantity`,
                        isExternal: true,
                      }}
                    >
                      Ajouter d’autres places et tarifs
                    </ButtonLink>
                  )}
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
        </FormLayout.Section>

        <div className={styles['action-buttons']}>
          <Button variant={ButtonVariant.SECONDARY} onClick={onCancel}>
            Annuler
          </Button>

          <SubmitButton
            Icon={CircleArrowIcon}
            iconPosition={IconPositionEnum.RIGHT}
          >
            Valider
          </SubmitButton>
        </div>
      </form>
    </FormikProvider>
  )
}
