import { useNavigate } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import useNotification from 'hooks/useNotification'
import AdagePreviewLayout from 'pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import publishCollectiveOfferTemplateAdapter from 'screens/CollectiveOfferSummaryCreation/adapters/publishCollectiveOfferTemplateAdapter'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface CollectiveOfferSummaryCreationProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  setOffer: (
    offer:
      | GetCollectiveOfferResponseModel
      | GetCollectiveOfferTemplateResponseModel
  ) => void
}

const CollectiveOfferPreviewCreationScreen = ({
  offer,
  setOffer,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()
  const navigate = useNavigate()

  const backRedirectionUrl = `/offre/${offer.id}/collectif/vitrine/creation/recapitulatif`

  const confirmationUrl = `/offre/${offer.id}/collectif/vitrine/confirmation`

  const publishOffer = async () => {
    const response = await publishCollectiveOfferTemplateAdapter(offer.id)

    if (!response.isOk) {
      notify.error(response.message)
      return
    }

    setOffer(response.payload)
    navigate(confirmationUrl)
  }

  return (
    <div>
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: backRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape précédente
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={publishOffer}>Publier l’offre</Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </div>
  )
}

export default CollectiveOfferPreviewCreationScreen
