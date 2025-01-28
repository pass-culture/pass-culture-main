import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOfferInformationsScreen } from './components/IndividualOfferInformationsScreen'

const IndividualOfferInformations = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      <IndividualOfferInformationsScreen offer={offer} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferInformations
