import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1/new'

type CollectiveOfferInformationsFormProps = {
  offer?: GetCollectiveOfferResponseModel
}

export const CollectiveOfferInformationsForm = ({
  offer,
}: CollectiveOfferInformationsFormProps): JSX.Element => {
  return (
    <div>
      <h1>{offer?.name}</h1>
    </div>
  )
}
