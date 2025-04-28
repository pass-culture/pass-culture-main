import { yupResolver } from '@hookform/resolvers/yup'
import { useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  TimeSpan,
} from 'apiClient/v1'
import { useNotification } from 'commons/hooks/useNotification'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import { weekDays } from '../../form/constants'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from '../../form/types'
import { validationSchema } from '../../form/validationSchema'
import {
  getStocksForMultipleDays,
  getStocksForOneDay,
  getWeekDayForDate,
} from '../utils'

import styles from './StocksCalendarForm.module.scss'
import { StocksCalendarFormFooter } from './StocksCalendarFormFooter/StocksCalendarFormFooter'
import { StocksCalendarFormMultipleDays } from './StocksCalendarFormMultipleDays/StocksCalendarFormMultipleDays'
import { StocksCalendarFormOneDay } from './StocksCalendarFormOneDay/StocksCalendarFormOneDay'

export type StocksCalendarFormProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  onAfterValidate: () => void
}

export function StocksCalendarForm({
  offer,
  onAfterValidate,
}: StocksCalendarFormProps) {
  const notify = useNotification()
  const form = useForm<StocksCalendarFormValues>({
    defaultValues: {
      durationType: DurationTypeOption.ONE_DAY,
      timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
      specificTimeSlots: [{ slot: '' }],
      openingHours: {},
      pricingCategoriesQuantities: [
        {
          isUnlimited: true,
          //  If there's only one price category, the default should be that one
          priceCategory:
            offer.priceCategories?.length === 1
              ? offer.priceCategories[0].id.toString()
              : undefined,
        },
      ],
      oneDayDate: '',
      multipleDaysStartDate: '',
      multipleDaysHasNoEndDate: false,
      multipleDaysWeekDays: [],
    },
    mode: 'onTouched',
    resolver: yupResolver(validationSchema),
  })

  useEffect(() => {
    //  When the checked week days change, update the list of time slots
    const subscription = form.watch((value, { name }) => {
      if (
        name === 'multipleDaysWeekDays' ||
        name === 'durationType' ||
        name === 'oneDayDate'
      ) {
        const weekDaysIncluded =
          value.durationType === DurationTypeOption.ONE_DAY && value.oneDayDate
            ? [getWeekDayForDate(new Date(value.oneDayDate)).value]
            : weekDays
                .map((d) => d.value)
                .filter((d) =>
                  value.multipleDaysWeekDays
                    ?.filter((wd) => wd?.checked)
                    .map((wd) => wd?.value)
                    .includes(d)
                )

        const newOpeningHours: StocksCalendarFormValues['openingHours'] = {}
        for (const day of weekDaysIncluded) {
          newOpeningHours[day] = (value.openingHours?.[day] || [
            { open: '', close: '' },
          ]) as TimeSpan[]
        }

        form.setValue('openingHours', newOpeningHours)
      }
    })
    return () => subscription.unsubscribe()
  }, [form, form.watch])

  const onSubmit = async () => {
    const departmentCode = getDepartmentCode(offer)
    const formValues = form.getValues()
    if (formValues.timeSlotType === TimeSlotTypeOption.SPECIFIC_TIME) {
      await onSubmitStocks({ formValues, departmentCode })
    } else {
      await onSubmitOpeningHours({ formValues, departmentCode })
    }

    onAfterValidate()
  }

  async function onSubmitStocks({
    formValues,
    departmentCode,
  }: {
    formValues: StocksCalendarFormValues
    departmentCode: string
  }) {
    const stocks =
      formValues.durationType === DurationTypeOption.ONE_DAY
        ? getStocksForOneDay(
            new Date(formValues.oneDayDate || ''),
            formValues,
            departmentCode
          )
        : getStocksForMultipleDays(formValues, departmentCode)

    try {
      const { stocks_count } = await api.upsertStocks({
        offerId: offer.id,
        stocks: stocks,
      })
      notify.success(
        stocks_count > 1
          ? `${new Intl.NumberFormat('fr-FR').format(
              stocks_count
            )} nouvelles dates ont été ajoutées`
          : `${stocks_count} nouvelle date a été ajoutée`
      )
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      notify.error(
        'Une erreur est survenue lors de l’enregistrement de vos stocks.'
      )
    }
  }

  async function onSubmitOpeningHours({
    formValues,
    departmentCode,
  }: {
    formValues: StocksCalendarFormValues
    departmentCode: string
  }) {
    if (!formValues.multipleDaysStartDate) {
      return;
    }
    try {
      await api.postEventOpeningHours(offer.id, {
        openingHours: formValues.openingHours,
        startDatetime: formValues.multipleDaysStartDate,
        endDatetime: formValues.multipleDaysEndDate,
      })
    }
    console.log('success')
  }

  return (
    <FormProvider {...form}>
      <form className={styles['form']} onSubmit={form.handleSubmit(onSubmit)}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <div className={styles['form-content']}>
          <MandatoryInfo />
          <RadioGroup
            name="durationType"
            variant={RadioVariant.BOX}
            displayMode="inline-grow"
            checkedOption={form.watch('durationType')}
            className={styles['duration-type-group']}
            onChange={(e) =>
              form.setValue(
                'durationType',
                e.target.value as DurationTypeOption
              )
            }
            group={[
              {
                label: '1 jour',
                value: DurationTypeOption.ONE_DAY,
                description:
                  'Planifiez un événement sur une journée entière ou une partie.',
              },
              {
                label: 'Plusieurs jours, semaines',
                value: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
                description:
                  'Planifier un événement sur plusieurs jours, semaines ou mois.',
              },
            ]}
            legend={
              <h2 className={styles['title']}>
                Votre évènement se déroule sur :
              </h2>
            }
          />
          {form.watch('durationType') === DurationTypeOption.ONE_DAY && (
            <StocksCalendarFormOneDay form={form} offer={offer} />
          )}
          {form.watch('durationType') ===
            DurationTypeOption.MULTIPLE_DAYS_WEEKS && (
            <StocksCalendarFormMultipleDays form={form} offer={offer} />
          )}
        </div>
        <DialogBuilder.Footer>
          <StocksCalendarFormFooter />
        </DialogBuilder.Footer>
      </form>
    </FormProvider>
  )
}
