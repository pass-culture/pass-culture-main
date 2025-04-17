import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { useNotification } from 'commons/hooks/useNotification'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { ScrollToFirstHookFormErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from '../../form/types'
import { validationSchema } from '../../form/validationSchema'
import { getStocksForMultipleDays, getStocksForOneDay } from '../utils'

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
  const form = useForm<StocksCalendarFormValues, any, any>({
    defaultValues: {
      durationType: DurationTypeOption.ONE_DAY,
      timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
      specificTimeSlots: [{ slot: '' }],
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
    resolver: yupResolver<StocksCalendarFormValues, any, any>(validationSchema),
  })

  const onSubmit = async () => {
    const departmentCode = getDepartmentCode(offer)
    const formValues = form.getValues()
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

    onAfterValidate()
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
