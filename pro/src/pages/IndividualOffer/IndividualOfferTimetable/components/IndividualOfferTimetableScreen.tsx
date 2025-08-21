import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  type GetOfferStockResponseModel,
  SubcategoryIdEnum,
  type WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { StocksThing } from '@/components/IndividualOffer/StocksThing/StocksThing'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'

import { areOpeningHoursEmpty } from '../commons/areOpeningHoursEmpty'
import type { IndividualOfferTimetableFormValues } from '../commons/types'
import { validationSchema } from '../commons/validationSchema'
import styles from './IndividualOfferTimetableScreen.module.scss'
import { TimetableOpeningHours } from './TimetableOpeningHours/TimetableOpeningHours'

type IndividualOfferTimetableScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
  openingHours?: WeekdayOpeningHoursTimespans | null
  stocks?: GetOfferStockResponseModel[]
}

const DISABLED_OPENING_HOURS_CATEGORIES: SubcategoryIdEnum[] = [
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
}: IndividualOfferTimetableScreenProps) {
  const isNewOfferCreationFlowFFEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const openingHoursEmpty = areOpeningHoursEmpty(openingHours)

  const form = useForm<IndividualOfferTimetableFormValues>({
    defaultValues: {
      timetableType: openingHoursEmpty ? 'calendar' : 'openingHours',
      openingHours: openingHours,
      startDate: undefined,
      noEndDate: true,
      quantityPerPriceCategories:
        !openingHoursEmpty && stocks && stocks.length > 0
          ? stocks.map((stock) => ({
              priceCategory: stock.priceCategoryId?.toString(),
              quantity: stock.quantity,
            }))
          : [{ priceCategory: offer.priceCategories?.[0].id.toString() || '' }],
    },
    resolver: yupResolver<IndividualOfferTimetableFormValues>(validationSchema),
    mode: 'onBlur',
  })

  if (!offer.isEvent) {
    return <StocksThing offer={offer} />
  }

  const shouldShowTimetableTypeRadioGroup =
    isNewOfferCreationFlowFFEnabled &&
    offer.isEvent &&
    !DISABLED_OPENING_HOURS_CATEGORIES.includes(offer.subcategoryId) &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    openingHoursEmpty &&
    !offer.hasStocks

  const timetableType = form.watch('timetableType')

  async function onSubmit(values: IndividualOfferTimetableFormValues) {
    const { startDate, quantityPerPriceCategories, openingHours } = values
    if (
      !startDate ||
      !quantityPerPriceCategories ||
      quantityPerPriceCategories.length === 0 ||
      !openingHours ||
      !stocks
    ) {
      return
    }

    try {
      await api.updateThingStock(stocks[0].id, {
        price:
          offer.priceCategories?.find(
            (cat) =>
              quantityPerPriceCategories[0].priceCategory === cat.id.toString()
          )?.price || 0,
        quantity: quantityPerPriceCategories[0].quantity,
      })

      const formattedOpeningHours = openingHours
      Object.entries(openingHours).forEach(([key, val]) => {
        const keyTmp = key as keyof WeekdayOpeningHoursTimespans
        formattedOpeningHours[keyTmp] =
          !formattedOpeningHours[keyTmp] ||
          formattedOpeningHours[keyTmp].length === 0
            ? null
            : formattedOpeningHours[keyTmp]
      })

      await api.upsertOfferOpeningHours(offer.id, {
        openingHours: formattedOpeningHours,
      })
    } catch {
      console.log('erreur')
    }
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {shouldShowTimetableTypeRadioGroup && (
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
            timetableTypeRadioGroupShown={shouldShowTimetableTypeRadioGroup}
          />
        )}
        {timetableType === 'openingHours' && (
          <TimetableOpeningHours
            offer={offer}
            mode={mode}
            timetableTypeRadioGroupShown={shouldShowTimetableTypeRadioGroup}
          />
        )}
      </form>
    </FormProvider>
  )
}
