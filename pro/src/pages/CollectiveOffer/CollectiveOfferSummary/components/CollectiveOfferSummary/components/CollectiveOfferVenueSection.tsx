import type { GetCollectiveOfferVenueResponseModel } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

export const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  return (
    <SummarySubSection
      title="Structure de rattachement de votre offre"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      <SummaryDescriptionList
        listDataTestId="summary-description-list"
        descriptions={[
          {
            title: 'Entité juridique',
            text: venue.managingOfferer.name,
          },
          {
            title: 'Structure',
            text: venue.publicName,
          },
        ]}
      />
    </SummarySubSection>
  )
}
