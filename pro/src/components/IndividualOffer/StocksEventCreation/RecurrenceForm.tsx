import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import {
  FormProvider,
  useFieldArray,
  useForm,
  useFormContext,
} from 'react-hook-form'

import { PriceCategoryResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { SelectOption } from 'commons/custom_types/form'
import { isDateValid, mapDayToFrench } from 'commons/utils/date'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioButtonGroup } from 'design-system/RadioButtonGroup/RadioButtonGroup'
import fullClearIcon from 'icons/full-clear.svg'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { DayCheckbox } from 'ui-kit/form/DayCheckbox/DayCheckbox'
import { QuantityInput } from 'ui-kit/form/QuantityInput/QuantityInput'
import { Select } from 'ui-kit/form/Select/Select'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import { getPriceCategoryOptions } from '../PriceCategoriesScreen/form/getPriceCategoryOptions'

import { computeInitialValues } from './form/computeInitialValues'
import { isLastWeekOfMonth } from './form/recurrenceUtils'
import {
  MonthlyOption,
  QuantityPerPriceCategoryForm,
  RecurrenceDays,
  RecurrenceFormValues,
  RecurrenceType,
} from './form/types'
import { getValidationSchema } from './form/validationSchema'
import styles from './RecurrenceForm.module.scss'

const INITIAL_QUANTITY_PER_PRICE_CATEGORY: QuantityPerPriceCategoryForm = {
  priceCategory: '',
}

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
  const startingDate = values.startingDate
    ? new Date(values.startingDate)
    : new Date()
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

const BeginningTimesForm = (): JSX.Element => {
  const { register, watch, formState } = useFormContext<RecurrenceFormValues>()

  const { fields, append, remove } = useFieldArray({
    name: 'beginningTimes',
  })

  return (
    <fieldset>
      <div className={styles['section']}>
        <h2 className={styles['legend']}>
          Horaires pour l’ensemble de ces dates
        </h2>

        <FormLayout.Row>
          <>
            <div className={styles['beginning-time-list']}>
              {fields.map((field, index) => (
                <div key={field.id} className={styles['time-slot']}>
                  <TimePicker
                    label={`Horaire ${index + 1}`}
                    className={styles['time-slot-picker']}
                    error={
                      formState.errors.beginningTimes?.[index]?.beginningTime
                        ?.message
                    }
                    {...register(`beginningTimes.${index}.beginningTime`)}
                    required
                  />
                  {watch('beginningTimes').length > 1 && (
                    <div className={styles['time-slot-clear']}>
                      <Tooltip content={`Supprimer l'horaire ${index + 1}`}>
                        <button
                          type="button"
                          className={styles['time-slot-clear-button']}
                          onClick={() => remove(index)}
                        >
                          <SvgIcon
                            alt={`Supprimer l'horaire ${index + 1}`}
                            src={fullClearIcon}
                            className={styles['time-slot-clear-button-icon']}
                          ></SvgIcon>
                        </button>
                      </Tooltip>
                    </div>
                  )}
                </div>
              ))}
            </div>
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullMoreIcon}
              onClick={() => {
                append('')
                const inputToFocus = `beginningTimes.${watch('beginningTimes').length}`

                // The input we want to focus has not been rendered yet
                setTimeout(() => {
                  document.getElementById(inputToFocus)?.focus()
                }, 0)
              }}
            >
              Ajouter un créneau
            </Button>
          </>
        </FormLayout.Row>
      </div>
    </fieldset>
  )
}

const PriceCategoriesForm = ({
  priceCategoryOptions,
}: {
  priceCategoryOptions: SelectOption[]
}): JSX.Element => {
  const { register, watch, setValue, formState } =
    useFormContext<RecurrenceFormValues>()

  const { fields, append, remove } = useFieldArray({
    name: 'quantityPerPriceCategories',
  })

  return (
    <fieldset>
      <div className={styles['section']}>
        <h2 className={styles['legend']}>Places et tarifs par horaire</h2>
        {fields.map((field, index) => (
          <FormLayout.Row
            key={field.id}
            inline
            mdSpaceAfter
            testId={`wrapper-quantityPerPriceCategories.${index}`}
          >
            <QuantityInput
              label="Nombre de places"
              className={styles['quantity-input']}
              minimum={1}
              name={`quantityPerPriceCategories.${index}.quantity`}
              error={
                formState.errors.quantityPerPriceCategories?.[index]?.quantity
                  ?.message
              }
              value={
                watch(`quantityPerPriceCategories.${index}.quantity`) ||
                undefined
              }
              onChange={(e) => {
                setValue(
                  `quantityPerPriceCategories.${index}.quantity`,
                  e.target.value ? Number(e.target.value) : undefined
                )
              }}
            />
            <Select
              label="Tarif"
              options={priceCategoryOptions}
              defaultOption={{
                label: 'Sélectionner un tarif',
                value: '',
              }}
              required
              error={
                formState.errors.quantityPerPriceCategories?.[index]
                  ?.priceCategory?.message
              }
              className={styles['price-category-input']}
              {...register(`quantityPerPriceCategories.${index}.priceCategory`)}
            />

            <div className={styles['align-icon']}>
              {watch('quantityPerPriceCategories').length > 1 && (
                <Button
                  variant={ButtonVariant.TERNARY}
                  icon={fullTrashIcon}
                  iconPosition={IconPositionEnum.CENTER}
                  onClick={() => remove(index)}
                  tooltipContent="Supprimer les places"
                />
              )}
            </div>
          </FormLayout.Row>
        ))}
        {watch('quantityPerPriceCategories').length <
          priceCategoryOptions.length && (
          <ButtonLink
            variant={ButtonVariant.TERNARY}
            icon={fullMoreIcon}
            onClick={() => append(INITIAL_QUANTITY_PER_PRICE_CATEGORY)}
            to={`#quantityPerPriceCategories[${
              watch('quantityPerPriceCategories').length - 1
            }].quantity`}
            isExternal
          >
            Ajouter d’autres places et tarifs
          </ButtonLink>
        )}
      </div>
    </fieldset>
  )
}

export const RecurrenceForm = ({
  priceCategories,
  handleSubmit,
}: RecurrenceFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()

  const priceCategoryOptions = getPriceCategoryOptions(priceCategories)

  const methods = useForm<RecurrenceFormValues>({
    defaultValues: computeInitialValues(priceCategoryOptions),
    resolver: yupResolver(getValidationSchema()),
    mode: 'onTouched',
  })

  const monthlyOptions = getMonthlyOptions(methods.watch())

  const onRecurrenceTypeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    methods.setValue('recurrenceType', e.target.value as RecurrenceType)
    methods.setValue('startingDate', '')
    methods.setValue('endingDate', '')
  }
  const startingDate = methods.watch('startingDate')
  const recurrenceType = methods.watch('recurrenceType')
  const minDateForEndingDate = isDateValid(startingDate)
    ? new Date(startingDate)
    : new Date()

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={(e) => {
          e.stopPropagation()
          e.preventDefault()
          return methods.handleSubmit(handleSubmit)(e)
        }}
        className={styles['form']}
        noValidate
      >
        <div className={styles['form-content']}>
          <div className={styles['mandatory']}>
            Tous les champs suivis d’un * sont obligatoires.
          </div>

          <div className={styles['recurrence-section']}>
            <RadioButtonGroup
              labelClassName={styles['legend-without-margin']}
              label="Cet évènement aura lieu"
              labelTag="h2"
              display="horizontal"
              options={[
                { label: 'Une seule fois', value: RecurrenceType.UNIQUE },
                { label: 'Tous les jours', value: RecurrenceType.DAILY },
                { label: 'Toutes les semaines', value: RecurrenceType.WEEKLY },
                { label: 'Tous les mois', value: RecurrenceType.MONTHLY },
              ]}
              variant="detailed"
              sizing="hug"
              name="recurrenceType"
              checkedOption={recurrenceType}
              onChange={onRecurrenceTypeChange}
            />
          </div>

          <fieldset>
            <div className={styles['section']}>
              {recurrenceType === RecurrenceType.WEEKLY && (
                <>
                  <div className={styles['day-inputs']}>
                    {Object.values(RecurrenceDays).map((day) => {
                      const frenchDay = mapDayToFrench(day)
                      return (
                        <DayCheckbox
                          key={day}
                          name={day}
                          label={frenchDay[0]}
                          tooltipContent={frenchDay}
                          checked={methods.watch('days').includes(day)}
                          onChange={(e) => {
                            let newDays = new Set(methods.watch('days'))
                            if (e.target.checked) {
                              newDays.add(day)
                            } else {
                              newDays.delete(day)
                            }
                            methods.setValue('days', Array.from(newDays))
                          }}
                        />
                      )
                    })}
                  </div>
                  {methods.formState.errors.days && (
                    <div className={styles['days-error']}>
                      <FieldError name="days">
                        {methods.formState.errors.days.message}
                      </FieldError>
                    </div>
                  )}
                </>
              )}
              {recurrenceType !== RecurrenceType.MONTHLY && (
                <FormLayout.Row inline>
                  <DatePicker
                    label={
                      recurrenceType === RecurrenceType.UNIQUE
                        ? 'Date de l’évènement'
                        : 'Du'
                    }
                    className={styles['date-input']}
                    minDate={new Date()}
                    error={methods.formState.errors.startingDate?.message}
                    required
                    {...methods.register('startingDate')}
                  />

                  {recurrenceType !== RecurrenceType.UNIQUE && (
                    <DatePicker
                      label="Au"
                      className={styles['date-input']}
                      minDate={minDateForEndingDate}
                      error={methods.formState.errors.endingDate?.message}
                      required
                      {...methods.register('endingDate')}
                    />
                  )}
                </FormLayout.Row>
              )}

              {recurrenceType === RecurrenceType.MONTHLY && (
                <FormLayout.Row inline>
                  <DatePicker
                    label={'Premier évènement le'}
                    className={styles['date-input']}
                    minDate={new Date()}
                    error={methods.formState.errors.startingDate?.message}
                    required
                    {...methods.register('startingDate')}
                  />

                  <Select
                    label="Détail de la récurrence"
                    options={monthlyOptions}
                    className={styles['monthly-option-input']}
                    defaultOption={{
                      label: 'Sélectionner une option',
                      value: '',
                    }}
                    required
                    error={methods.formState.errors.monthlyOption?.message}
                    {...methods.register('monthlyOption')}
                  />

                  <DatePicker
                    label="Fin de la récurrence"
                    className={styles['date-input']}
                    minDate={minDateForEndingDate}
                    error={methods.formState.errors.endingDate?.message}
                    required
                    {...methods.register('endingDate')}
                  />
                </FormLayout.Row>
              )}
            </div>
          </fieldset>

          <BeginningTimesForm />

          <PriceCategoriesForm priceCategoryOptions={priceCategoryOptions} />

          <fieldset>
            <div className={styles['section']}>
              <h2 className={styles['legend']}>Date limite de réservation</h2>

              <div className={styles['booking-date-limit-container']}>
                <TextInput
                  label="Date limite de réservation (en nombre de jours avant le début de l’évènement)"
                  isLabelHidden
                  type="number"
                  step="1"
                  min={0}
                  className={styles['booking-date-limit-input']}
                  error={
                    methods.formState.errors.bookingLimitDateInterval?.message
                  }
                  {...methods.register('bookingLimitDateInterval')}
                  onBlur={() => {
                    const bookingLimitDateInterval = methods.watch(
                      'bookingLimitDateInterval'
                    )
                    if (bookingLimitDateInterval) {
                      logEvent(Events.UPDATED_BOOKING_LIMIT_DATE, {
                        from: location.pathname,
                        bookingLimitDateInterval: bookingLimitDateInterval,
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
              disabled={methods.formState.isSubmitting}
              isLoading={methods.formState.isSubmitting}
            >
              Valider
            </Button>
          </div>
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
