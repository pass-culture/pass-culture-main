import { useEffect } from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { UsefulInformationScreen } from 'screens/IndividualOffer/UsefulInformationScreen/UsefulInformationScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const UsefulInformation = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  // Required for the step above the frame to return to the top of the page
  // TODO: Change to useFocus when we find a solution for the scroll
  useEffect(() => {
    document.getElementById('content-wrapper')?.scrollTo(0, 0)
  }, [])

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <UsefulInformationScreen offer={offer} />
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = UsefulInformation
