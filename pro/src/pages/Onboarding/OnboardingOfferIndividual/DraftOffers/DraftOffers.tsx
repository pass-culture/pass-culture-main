import { api } from 'apiClient/api'
import {
  CategoryResponseModel,
  ListOffersOfferResponseModel,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { GET_CATEGORIES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import strokOfferIcon from 'icons/stroke-offer.svg'
import { CardLink } from 'pages/Onboarding/OnboardingOfferIndividual/CardLink/CardLink'
import useSWR from 'swr'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './DraftOffers.module.scss'

interface DraftOffersProps {
  offers: ListOffersOfferResponseModel[]
}

const extractOfferCategoriesData = (
  offer: ListOffersOfferResponseModel,
  categories: CategoryResponseModel[],
  subcategories: SubcategoryResponseModel[]
) => {
  const subcategory = subcategories.find((s) => s.id === offer.subcategoryId)
  const category = categories.find((c) => c.id === subcategory?.categoryId)
  return { category, subcategory }
}

export const DraftOffers = ({ offers }: DraftOffersProps): JSX.Element => {
  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  if (categoriesQuery.isLoading) {
    return <Spinner />
  }

  const categories = categoriesQuery.data.categories
  const subcategories = categoriesQuery.data.subcategories

  return (
    <>
      <h2 className={styles['title-drafts']}>
        Reprendre une offre déjà commencée
      </h2>

      <div data-testid="draft-offers">
        {offers.map((offer) => {
          const { category, subcategory } = extractOfferCategoriesData(
            offer,
            categories,
            subcategories
          )
          const categoryLabel = `${category?.proLabel} - ${subcategory?.proLabel}`

          return (
            <CardLink
              to={`/onboarding/offre/individuelle/${offer.id}/creation/details`}
              className={styles['offer']}
              key={offer.id}
              label={offer.name}
              description={categoryLabel}
              direction="horizontal"
              icon={strokOfferIcon}
            />
          )
        })}
      </div>
    </>
  )
}
