import type { GetCollectiveOfferVenueResponseModel } from '@/apiClient/v1'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

export const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
  return (
    <SummarySubSection title="Structure de rattachement de votre offre">
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
