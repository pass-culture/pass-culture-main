import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'

import { timetableFormDefaultValues } from '../commons/timetableFormDefaultValues'
import type { IndividualOfferTimetableFormValues } from '../commons/types'
import { validationSchema } from '../commons/validationSchema'

export type IndividualOfferTimetableScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
}

export function IndividualOfferTimetableScreen({
  offer,
  mode,
}: IndividualOfferTimetableScreenProps) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const form = useForm<IndividualOfferTimetableFormValues>({
    defaultValues: timetableFormDefaultValues,
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  function handleNextStep() {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
      return
    }
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
        isOnboarding,
      })
    )
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(handleNextStep)}>
        <StocksCalendar offer={offer} mode={mode} />
      </form>
    </FormProvider>
  )
}
