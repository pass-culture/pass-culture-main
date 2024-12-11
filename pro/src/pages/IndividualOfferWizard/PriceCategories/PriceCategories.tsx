import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { PriceCategoriesScreen } from 'components/IndividualOffer/PriceCategoriesScreen/PriceCategoriesScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const PriceCategories = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  // Offer might be null: when we submit Informations form, we setOffer with the
  // submited payload. Due to React 18 render batching behavior and react-router
  // implementation, this component can be rendered before the offer is set in the
  // offer individual context
  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <PriceCategoriesScreen offer={offer} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = PriceCategories
