import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'
import { getStockWarningText } from '@/pages/IndividualOfferSummary/commons/getStockWarningText'

type StocksCalendarSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryStocksCalendarScreen({
  offer,
}: Readonly<StocksCalendarSummaryScreenProps>) {
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: isNewOfferCreationFlowFeatureActive
      ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
      : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  return (
    <SummarySection
      title={
        isNewOfferCreationFlowFeatureActive ? 'Horaires' : 'Dates et capacités'
      }
      editLink={editLink}
      aria-label="Modifier le calendrier"
    >
      {getStockWarningText(offer)}

      <StocksCalendar
        offer={offer}
        mode={OFFER_WIZARD_MODE.READ_ONLY}
        timetableTypeRadioGroupShown={false}
      />
    </SummarySection>
  )
}
