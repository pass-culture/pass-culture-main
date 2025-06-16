import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'

export type BookableOfferSummaryProps = {
  offer: GetCollectiveOfferResponseModel
}

export const BookableOfferSummary = ({ offer }: BookableOfferSummaryProps) => {
  return (
    <Layout layout={'sticky-actions'}>
      <div>
        <p>
          Nouveau composant de recap pour une offre réservable : Work in
          progress
        </p>
        <p>{offer.name}</p>
      </div>
    </Layout>
  )
}
