import type React from 'react'
import { useFormContext } from 'react-hook-form'

import {
  Mode,
  type OfferEducationalStockFormValues,
} from '@/commons/core/OfferEducational/types'
import { isDateValid } from '@/commons/utils/date'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullHelpIcon from '@/icons/full-help.svg'
import strokeCollaborator from '@/icons/stroke-collaborator.svg'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

import {
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  START_DATE_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'
import styles from './FormStock.module.scss'

export interface FormStockProps {
  mode: Mode
  canEditDiscount: boolean
  canEditDates: boolean
  preventPriceIncrease: boolean
}

export const FormStock = ({
  mode,
  canEditDiscount,
  canEditDates,
}: FormStockProps): JSX.Element => {
  const { watch, setValue, register, formState } =
    useFormContext<OfferEducationalStockFormValues>()

  const values = watch()

  const minEndDatetime = isDateValid(values.startDatetime)
    ? new Date(values.startDatetime)
    : new Date()

  function handleStartDatetimeChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    setValue('startDatetime', event.target.value, { shouldValidate: true })
    if (mode === Mode.EDITION || mode === Mode.CREATION) {
      if (
        !isDateValid(values.endDatetime) ||
        values.endDatetime < event.target.value
      ) {
        setValue('endDatetime', event.target.value, { shouldValidate: true })
      }
    }
  }

  return (
    <FormLayout.Row inline className={styles['layout-row']}>
      <DatePicker
        disabled={!canEditDates}
        label={START_DATE_LABEL}
        minDate={new Date()}
        {...register('startDatetime')}
        onChange={handleStartDatetimeChange}
        error={formState.errors.startDatetime?.message}
        className={styles['input-date']}
        required
        asterisk={false}
      />
      <DatePicker
        disabled={!canEditDates}
        label={
          <span className={styles['label-container']}>
            Date de fin
            <Tooltip content="Le remboursement de votre offre sera effectué 2 à 3 semaines après la fin de votre évènement.">
              <button type="button" className={styles['help-button']}>
                <SvgIcon src={fullHelpIcon} />
              </button>
            </Tooltip>
          </span>
        }
        minDate={minEndDatetime}
        className={styles['input-date']}
        required
        asterisk={false}
        {...register('endDatetime')}
        error={formState.errors.endDatetime?.message}
      />
      <TimePicker
        disabled={!canEditDates}
        label={EVENT_TIME_LABEL}
        {...register('eventTime')}
        error={formState.errors.eventTime?.message}
        className={styles['custom-field-layout']}
        required
        asterisk={false}
      />
      <TextInput
        disabled={!canEditDiscount}
        label={NUMBER_OF_PLACES_LABEL}
        {...register('numberOfPlaces')}
        error={formState.errors.numberOfPlaces?.message}
        type="number"
        icon={strokeCollaborator}
        required
        asterisk={false}
      />
      <TextInput
        disabled={!canEditDiscount}
        label={`${TOTAL_PRICE_LABEL} (en €)`}
        {...register('totalPrice')}
        error={formState.errors.totalPrice?.message}
        step={0.01} // allow user to enter a price with cents
        min={0}
        type="number"
        required
        asterisk={false}
      />
    </FormLayout.Row>
  )
}
