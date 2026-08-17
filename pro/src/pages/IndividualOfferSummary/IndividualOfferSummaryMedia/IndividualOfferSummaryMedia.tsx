import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { INDIVIDUAL_OFFER_WIZARD_STEP_IDS } from '@/commons/core/Offers/constants'
import { getIndividualOfferImage } from '@/commons/core/Offers/utils/getIndividualOfferImage'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'
import { MediaSection } from '@/pages/IndividualOfferSummary/components/MediaSection/MediaSection'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SummaryContent } from '@/ui-kit/SummaryLayout/SummaryContent'
import { SummaryLayout } from '@/ui-kit/SummaryLayout/SummaryLayout'

const IndividualOfferSummaryMedia = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const image = getIndividualOfferImage(offer)

  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <SummaryLayout>
        <SummaryContent>
          <MediaSection
            offerId={offer.id}
            imageUrl={image?.url}
            imageCredit={image?.credit}
            videoData={offer.videoData}
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
