import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { StocksCalendar } from '@/pages/IndividualOffer/IndividualOfferTimetable/components/StocksCalendar/StocksCalendar'
import { getStockWarningText } from '@/pages/IndividualOfferSummary/commons/getStockWarningText'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'

type StocksCalendarSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function IndividualOfferSummaryStocksCalendarScreen({
  offer,
}: Readonly<StocksCalendarSummaryScreenProps>) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  return (
    <SummarySection
      title="Horaires et stocks"
      editLink={editLink}
      aria-label="Modifier le calendrier"
      isReadOnly={withVenueHelpers(selectedPartnerVenue).isClosed}
    >
      {getStockWarningText(offer)}

      <StocksCalendar offer={offer} mode={OFFER_WIZARD_MODE.READ_ONLY} />
    </SummarySection>
  )
}
