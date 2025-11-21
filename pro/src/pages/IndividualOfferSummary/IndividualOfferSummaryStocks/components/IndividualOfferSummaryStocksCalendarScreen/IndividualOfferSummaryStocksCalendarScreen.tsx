import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'
import { getStockWarningText } from '@/pages/IndividualOfferSummary/commons/getStockWarningText'

type StocksCalendarSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryStocksCalendarScreen({
  offer,
}: Readonly<StocksCalendarSummaryScreenProps>) {
  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  return (
    <SummarySection
      title="Horaires"
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
