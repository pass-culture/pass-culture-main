import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferType,
} from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { createOfferFromTemplate } from 'commons/core/OfferEducational/utils/createOfferFromTemplate'
import { DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { GET_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOfferer } from 'commons/store/offerer/selectors'
import { pluralize } from 'commons/utils/pluralize'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CollectiveOfferSelectionDuplication.module.scss'
import { SkeletonLoader } from './CollectiveOfferSelectionLoaderSkeleton'

type SearchFormValues = {
  searchFilter: string
}

type SelectionFormValues = {
  templateOfferId: string
}

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )

  const searchFilterForm = useForm<SearchFormValues>({
    defaultValues: { searchFilter: '' },
  })

  const { register: registerSearch, handleSubmit: handleSubmitSearch } =
    searchFilterForm

  const queryParams = new URLSearchParams(location.search)
  const currentOfferer = useSelector(selectCurrentOfferer)
  const queryOffererId = currentOfferer?.id ?? null
  const queryVenueId = queryParams.get('lieu')

  const {
    nameOrIsbn,
    offererId,
    venueId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
    format,
  } = serializeApiCollectiveFilters(
    {
      ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
      nameOrIsbn: searchFilterForm.watch('searchFilter'),
      offererId: queryOffererId ? queryOffererId.toString() : 'all',
      venueId: queryVenueId ? queryVenueId : 'all',
      status: [
        CollectiveOfferDisplayedStatus.PUBLISHED,
        CollectiveOfferDisplayedStatus.HIDDEN,
        CollectiveOfferDisplayedStatus.ENDED,
      ],
    },
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
  )

  const {
    data: offers,
    error,
    isLoading,
  } = useSWR([GET_COLLECTIVE_OFFERS_QUERY_KEY, nameOrIsbn], () =>
    api.getCollectiveOffers(
      nameOrIsbn,
      offererId,
      status,
      venueId,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
      CollectiveOfferType.TEMPLATE,
      format
    )
  )

  const templateOfferForm = useForm<SelectionFormValues>()

  useEffect(() => {
    if (!isLoading && offers && offers.length > 0) {
      templateOfferForm.setValue('templateOfferId', String(offers[0].id))
    }
  }, [offers, isLoading, templateOfferForm])

  const { handleSubmit: handleSubmitSelection } = templateOfferForm

  const handleOnSubmit = async () => {
    const templateOfferId = templateOfferForm.watch('templateOfferId')

    await createOfferFromTemplate(
      navigate,
      notify,
      Number(templateOfferId),
      isCollectiveOaActive,
      undefined,
      isMarseilleActive
    )
  }

  return (
    <Layout layout={'sticky-actions'} mainHeading="Créer une offre réservable">
      <div className="container">
        <div className={styles['search-container']}>
          <form
            className={styles['search-input-container']}
            aria-labelledby="search-filter"
            onSubmit={handleSubmitSearch(({ searchFilter }) => {
              searchFilterForm.setValue('searchFilter', searchFilter)
              templateOfferForm.setValue(
                'templateOfferId',
                String(offers?.[0]?.id)
              )

              if (error) {
                return notify.error(GET_DATA_ERROR_MESSAGE)
              }
            })}
          >
            <TextInput
              label="Rechercher l’offre vitrine à dupliquer"
              {...registerSearch('searchFilter')}
              name="searchFilter"
              type="search"
              autoComplete="off"
              onChange={(e) => {
                if (e.target.value === '') {
                  searchFilterForm.setValue('searchFilter', e.target.value)
                }
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  searchFilterForm.setValue(
                    'searchFilter',
                    (e.target as HTMLInputElement).value
                  )
                }
              }}
              className={styles['search-input']}
              InputExtension={
                <Button
                  type="submit"
                  className={styles['search-button']}
                  disabled={isLoading}
                >
                  Rechercher
                </Button>
              }
            />
          </form>

          {isLoading ? (
            <SkeletonLoader />
          ) : (
            <form onSubmit={handleSubmitSelection(handleOnSubmit)}>
              <RadioGroup
                name="templateOfferId"
                variant="detailed"
                legend={
                  <>
                    <p className={styles['offers-description']}>
                      {searchFilterForm.watch('searchFilter').length < 1
                        ? 'Les dernières offres vitrines créées'
                        : `${offers && pluralize(offers.length, 'offre')}` +
                          ' vitrine'}
                    </p>
                    <p className={styles['visually-hidden']} role="status">
                      {offers &&
                        pluralize(offers.length, 'offre vitrine trouvée')}
                    </p>
                  </>
                }
                group={
                  offers
                    ? offers.slice(0, 5).map((offer) => ({
                        value: offer.id.toString(),
                        label: offer.name,
                        description: offer.venue.name,
                        variant: 'detailed',
                        image: offer.imageUrl as string,
                        imageSize: 'm',

                        sizing: 'fill',
                      }))
                    : []
                }
                checkedOption={templateOfferForm.watch('templateOfferId')}
                onChange={(e) => {
                  templateOfferForm.setValue('templateOfferId', e.target.value)
                }}
              />
              {offers && offers.length < 1 && (
                <div className={styles['search-no-results']}>
                  <SvgIcon
                    src={strokeSearchIcon}
                    alt="Illustration de recherche"
                    className={styles['search-no-results-icon']}
                    width="124"
                  />
                  <p className={styles['search-no-results-text']}>
                    Aucune offre trouvée pour votre recherche
                  </p>
                </div>
              )}

              <ActionsBarSticky>
                <ActionsBarSticky.Left>
                  <ButtonLink
                    variant={ButtonVariant.SECONDARY}
                    to={computeCollectiveOffersUrl({})}
                  >
                    Annuler et quitter
                  </ButtonLink>
                </ActionsBarSticky.Left>
                <ActionsBarSticky.Right>
                  <Button type="submit" disabled={false}>
                    Étape suivante
                  </Button>
                </ActionsBarSticky.Right>
              </ActionsBarSticky>
            </form>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferSelectionDuplication
