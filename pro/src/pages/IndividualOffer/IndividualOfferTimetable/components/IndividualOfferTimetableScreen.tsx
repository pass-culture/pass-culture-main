import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  type GetOfferStockResponseModel,
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
import { useNotification } from '@/commons/hooks/useNotification'
import { StocksThing } from '@/components/IndividualOffer/StocksThing/StocksThing'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'
import { cleanOpeningHours } from '@/pages/VenueEdition/serializers'

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
  stocks: GetOfferStockResponseModel[]
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
  stocks,
  venue,
}: IndividualOfferTimetableScreenProps) {
  const isNewOfferCreationFlowFFEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const isOhoFFEnabled = useActiveFeature('WIP_ENABLE_OHO')

  const notify = useNotification()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const form = useForm<IndividualOfferTimetableFormValues>({
    defaultValues: getTimetableFormDefaultValues({
      openingHours,
      venueOpeningHours: venue?.openingHours,
      stocks,
      offer,
      isOhoFFEnabled,
    }),
    resolver: yupResolver<IndividualOfferTimetableFormValues, unknown, unknown>(
      validationSchema
    ),
    mode: 'onBlur',
  })

  if (!offer.isEvent) {
    return <StocksThing offer={offer} />
  }

  const isOfferTimetableTypeEditable =
    isNewOfferCreationFlowFFEnabled &&
    isOhoFFEnabled &&
    offer.isEvent &&
    !DISABLED_OPENING_HOURS_SUBCATEGORIES.includes(offer.subcategoryId) &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    areOpeningHoursEmpty(openingHours) &&
    !offer.hasStocks

  const timetableType = form.watch('timetableType')

  async function onSubmit(values: IndividualOfferTimetableFormValues) {
    const { quantityPerPriceCategories, openingHours } = values

    if (
      !quantityPerPriceCategories ||
      quantityPerPriceCategories.length === 0 ||
      !openingHours ||
      timetableType === 'calendar'
    ) {
      return
    }

    try {
      //  TODO : Enable the creation of the stock when the api can create a thingStock for a "isThing" offer ie: subcategory is not event
      /*  const { quantity, priceCategory } = quantityPerPriceCategories[0]

      const price =
        offer.priceCategories?.find(
          (cat) => priceCategory === cat.id.toString()
        )?.price || 0

      const stockBody = { price, quantity }

      if (stocks && stocks.length > 0) {
        await api.updateThingStock(stocks[0].id, stockBody)
      } else {
        await api.createThingStock({ ...stockBody, offerId: offer.id })
      } */

      await api.upsertOfferOpeningHours(offer.id, {
        //  TODO : update startDate and endDate here when it's available on the openingHours api
        openingHours: cleanOpeningHours(openingHours),
      })

      await mutate([GET_OFFER_OPENING_HOURS_QUERY_KEY, offer.id])

      handleNextStep()
    } catch {
      notify.error(SENT_DATA_ERROR_MESSAGE)
    }
  }

  function handleNextStep() {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
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
              label="Quand profiter de l’offre&nbsp;?"
              name="timetableType"
              labelTag="h2"
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
