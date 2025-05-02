/* istanbul ignore file */
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { PriceCategoriesSection } from 'components/IndividualOffer/SummaryScreen/PriceCategoriesSection/PriceCategoriesSection'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const PriceCategoriesSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, subCategories } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = PriceCategoriesSummary
