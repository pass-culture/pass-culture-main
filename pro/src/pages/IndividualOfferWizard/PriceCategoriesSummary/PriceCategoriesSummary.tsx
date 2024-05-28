/* istanbul ignore file */
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { PriceCategoriesSection } from 'screens/IndividualOffer/SummaryScreen/PriceCategoriesSection/PriceCategoriesSection'
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
    <IndivualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = PriceCategoriesSummary
