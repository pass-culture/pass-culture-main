import type {
  GetIndividualOfferWithAddressResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import { OpeningHoursReadOnly } from '@/pages/VenueEdition/OpeningHoursAndAddressReadOnly/OpeningHoursReadOnly'

type IndividualOfferSummaryStocksTimetableScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  openingHours: WeekdayOpeningHoursTimespans
}

export function IndividualOfferSummaryStocksTimetableScreen({
  offer,
  openingHours,
}: Readonly<IndividualOfferSummaryStocksTimetableScreenProps>) {
  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  //    TODO : add dates section when openingHours have start and end dates
  return (
    <SummarySection title="Horaires" editLink={editLink}>
      <SummarySubSection title="Horaires d’accès ">
        <OpeningHoursReadOnly openingHours={openingHours} />
      </SummarySubSection>
    </SummarySection>
  )
}
