import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from 'commons/core/Offers/constants'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from 'components/IndividualOfferLayout/IndividualOfferLayout'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { MediaSection } from 'pages/IndividualOfferSummary/components/MediaSection/MediaSection'
import { Spinner } from 'ui-kit/Spinner/Spinner'

const IndividualOfferSummaryMedia = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <SummaryLayout>
        <SummaryContent>
          <MediaSection
            offerId={offer.id}
            imageUrl={offer.thumbUrl}
            videoUrl={offer.videoUrl}
          />
        </SummaryContent>
      </SummaryLayout>
      <ActionBar
        step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryMedia
