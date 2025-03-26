import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { IndividualOfferInformationsScreen } from './components/IndividualOfferInformationsScreen'

const IndividualOfferInformations = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      {!offer ? (
        <Spinner />
      ) : (
        <IndividualOfferInformationsScreen offer={offer} />
      )}
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferInformations
