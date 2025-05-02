import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
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
    <IndividualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <PriceCategoriesScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = PriceCategories
