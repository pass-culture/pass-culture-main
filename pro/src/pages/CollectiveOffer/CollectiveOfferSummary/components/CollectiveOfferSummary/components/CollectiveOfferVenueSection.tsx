
import { GetCollectiveOfferVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferSummaryProps {
  venue: GetCollectiveOfferVenueResponseModel
}

export const CollectiveOfferVenueSection = ({
  venue,
}: CollectiveOfferSummaryProps) => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <SummarySubSection
      title={
        isOfferAddressEnabled
          ? 'Structure de rattachement de votre offre'
          : 'Lieu de rattachement de votre offre'
      }
    >
      <SummaryDescriptionList
        listDataTestId="summary-description-list"
        descriptions={[
          {
            title: `${isOfferAddressEnabled ? 'Entité juridique' : 'Structure'}`,
            text: venue.managingOfferer.name,
          },
          {
            title: `${isOfferAddressEnabled ? 'Structure' : 'Lieu'}`,
            text: venue.publicName || venue.name,
          },
        ]}
      />
    </SummarySubSection>
  )
}
