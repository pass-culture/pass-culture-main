import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { getStockWarningText } from '@/pages/IndividualOfferSummary/commons/getStockWarningText'
import { PriceCategoriesSection } from '@/pages/IndividualOfferSummary/components/PriceCategoriesSection/PriceCategoriesSection'
import { StockThingSection } from '@/pages/IndividualOfferSummary/components/StockThingSection/StockThingSection'

interface IndividualOfferSummaryPriceTableScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
  offerStocks: GetOfferStockResponseModel[]
}
export const IndividualOfferSummaryPriceTableScreen = ({
  offer,
  offerStocks,
}: IndividualOfferSummaryPriceTableScreenProps) => {
  const { subCategories } = useIndividualOfferContext()

  const offerSubcategory = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )
  assertOrFrontendError(
    offerSubcategory,
    `\`offerSubcategory\` not found in subcategories ("${offer.subcategoryId}").`
  )

  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })
  const stockWarningText = getStockWarningText(offer)

  if (offer.isEvent) {
    return (
      <PriceCategoriesSection
        canBeDuo={offerSubcategory.canBeDuo}
        offer={offer}
      />
    )
  }

  return (
    <SummarySection
      title="Tarifs"
      editLink={editLink}
      aria-label="Modifier les tarifs"
    >
      {stockWarningText && (
        <SummaryDescriptionList descriptions={[{ text: stockWarningText }]} />
      )}

      <StockThingSection
        stock={offerStocks[0]}
        canBeDuo={offerSubcategory.canBeDuo}
        isDuo={offer.isDuo}
      />
    </SummarySection>
  )
}
