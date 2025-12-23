import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  type GetVenueResponseModel,
  SubcategoryIdEnum,
  type WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import { GET_OFFER_OPENING_HOURS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'
import { cleanOpeningHours } from '@/pages/VenueEdition/commons/serializers'

import { areOpeningHoursEmpty } from '../commons/areOpeningHoursEmpty'
import { getTimetableFormDefaultValues } from '../commons/getTimetableFormDefaultValues'
import type { IndividualOfferTimetableFormValues } from '../commons/types'
import { validationSchema } from '../commons/validationSchema'
import styles from './IndividualOfferTimetableScreen.module.scss'
import { TimetableOpeningHours } from './TimetableOpeningHours/TimetableOpeningHours'

export type IndividualOfferTimetableScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
  openingHours?: WeekdayOpeningHoursTimespans | null
  venue?: GetVenueResponseModel
}

//  TODO : have this info on the subcategories in the back
const DISABLED_OPENING_HOURS_SUBCATEGORIES: SubcategoryIdEnum[] = [
  SubcategoryIdEnum.FESTIVAL_SPECTACLE,
  SubcategoryIdEnum.FESTIVAL_MUSIQUE,
  SubcategoryIdEnum.FESTIVAL_ART_VISUEL,
  SubcategoryIdEnum.FESTIVAL_CINE,
  SubcategoryIdEnum.FESTIVAL_LIVRE,
]

export function IndividualOfferTimetableScreen({
  offer,
  mode,
  openingHours,
  venue,
}: IndividualOfferTimetableScreenProps) {
  const isOhoFFEnabled = useActiveFeature('WIP_ENABLE_OHO')

  const snackBar = useSnackBar()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const form = useForm<IndividualOfferTimetableFormValues>({
    defaultValues: getTimetableFormDefaultValues({
      openingHours,
      venueOpeningHours: venue?.openingHours,
      isOhoFFEnabled,
    }),
    resolver: yupResolver(validationSchema),
    mode: 'onBlur',
  })

  const isOfferTimetableTypeEditable =
    isOhoFFEnabled &&
    offer.isEvent &&
    !DISABLED_OPENING_HOURS_SUBCATEGORIES.includes(offer.subcategoryId) &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    areOpeningHoursEmpty(openingHours) &&
    !offer.hasStocks

  const timetableType = form.watch('timetableType')

  async function onSubmit(values: IndividualOfferTimetableFormValues) {
    const { openingHours } = values

    if (!openingHours || timetableType === 'calendar') {
      return
    }

    try {
      await api.upsertOfferOpeningHours(offer.id, {
        //  TODO : update startDate and endDate here when it's available on the openingHours api
        openingHours: cleanOpeningHours(openingHours),
      })

      await mutate([GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id])

      handleNextStep()
    } catch {
      snackBar.error(SENT_DATA_ERROR_MESSAGE)
    }
  }

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
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {isOfferTimetableTypeEditable && (
          <div className={styles['group']}>
            <RadioButtonGroup
              label={
                <h2 className={styles['radio-group-title']}>
                  Quand profiter de l’offre&nbsp;?
                </h2>
              }
              name="timetableType"
              variant="detailed"
              display="horizontal"
              checkedOption={timetableType}
              onChange={(event) => {
                form.setValue(
                  'timetableType',
                  event.target
                    .value as IndividualOfferTimetableFormValues['timetableType']
                )
              }}
              options={[
                {
                  label: 'À des horaires précis',
                  value: 'calendar',
                  description:
                    "Le jeune doit impérativement se présenter à l'horaire précis mentionné sur sa réservation.",
                },
                {
                  label: 'Librement',
                  value: 'openingHours',
                  description:
                    "Le jeune peut se présenter quand il le souhaite sur des plages horaires, par exemple vos horaires d'ouverture.",
                },
              ]}
            />
          </div>
        )}
        {timetableType === 'calendar' && (
          <StocksCalendar
            offer={offer}
            mode={mode}
            timetableTypeRadioGroupShown={isOfferTimetableTypeEditable}
          />
        )}
        {timetableType === 'openingHours' && (
          <TimetableOpeningHours
            offer={offer}
            mode={mode}
            timetableTypeRadioGroupShown={isOfferTimetableTypeEditable}
          />
        )}
      </form>
    </FormProvider>
  )
}
