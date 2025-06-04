import { Form, FormikProvider, useFormik } from 'formik'
import { useCallback, useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferType,
} from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import { createOfferFromTemplate } from 'commons/core/OfferEducational/utils/createOfferFromTemplate'
import { DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { computeCollectiveOffersUrl } from 'commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from 'commons/core/Offers/utils/serializer'
import { GET_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { pluralize } from 'commons/utils/pluralize'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CollectiveOfferSelectionDuplication.module.scss'

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const [offers, setOffers] = useState<CollectiveOfferResponseModel[]>([])
  const [showAll, setShowAll] = useState(true)
  const notify = useNotification()
  const navigate = useNavigate()
  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )
  const formikSearch = useFormik({
    initialValues: { searchFilter: '' },
    onSubmit: (formValues) =>
      filterTemplateOfferByName(formValues.searchFilter),
  })
  const formikSelection = useFormik({
    initialValues: { templateOfferId: '' },
    onSubmit: () => handleOnSubmit(),
  })
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = useSelector(selectCurrentOffererId)
  const queryVenueId = queryParams.get('lieu')

  const filterTemplateOfferByName = useCallback(
    async (offerName: string) => {
      setIsLoading(true)
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
          nameOrIsbn: offerName,
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
      try {
        const offers = await api.getCollectiveOffers(
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

        if (offerName.length < 1) {
          setShowAll(true)
        } else {
          setShowAll(false)
        }

        setOffers(offers)
        await formikSelection.setFieldValue(
          'templateOfferId',
          String(offers[0].id)
        )
        setIsLoading(false)
      } catch {
        setIsLoading(false)
        return notify.error(GET_DATA_ERROR_MESSAGE)
      }
    },
    [notify]
  )

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    filterTemplateOfferByName(formikSearch.initialValues.searchFilter)
  }, [formikSearch.initialValues.searchFilter])

  const handleOnSubmit = () => {
    const templateOfferId = formikSelection.values.templateOfferId
    if (templateOfferId === '') {
      return notify.error(
        'Vous devez sélectionner une offre vitrine à dupliquer'
      )
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    createOfferFromTemplate(
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
        <h2 className={styles['sub-title']} id="search-filter">
          Rechercher l’offre vitrine à dupliquer
        </h2>

        <div className={styles['search-container']}>
          {isLoading ? (
            <Spinner />
          ) : (
            <>
              <FormikProvider value={formikSearch}>
                <Form className={styles['search-input-container']}>
                  <TextInput
                    label="Offre vitrine à dupliquer"
                    isLabelHidden
                    name="searchFilter"
                    type="search"
                    className={styles['search-input']}
                    aria-labelledby="search-filter"
                    isOptional
                  />
                  <Button
                    type="submit"
                    className={styles['search-button']}
                    isLoading={isLoading}
                  >
                    Rechercher
                  </Button>
                </Form>
              </FormikProvider>
              <FormikProvider value={formikSelection}>
                <Form>
                  <RadioGroup
                    variant="detailed"
                    legend={
                      <>
                        <p>
                          {showAll
                            ? 'Les dernières offres vitrines créées'
                            : `${pluralize(offers.length, 'offre')} vitrine`}
                        </p>
                        <p className={styles['visually-hidden']} role="status">
                          {pluralize(offers.length, 'offre vitrine trouvée')}
                        </p>
                      </>
                    }
                    group={offers.slice(0, 5).map((offer) => ({
                      value: offer.id.toString(),
                      label: offer.name,
                      description: offer.venue.name,
                      variant: 'detailed',
                      image: offer.imageUrl as string,
                      imageSize: 'm',

                      sizing: 'fill',
                    }))}
                    name="templateOfferId"
                    checkedOption={formikSelection.values.templateOfferId}
                    onChange={formikSelection.handleChange}
                  />
                  {offers.length < 1 && (
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
                </Form>
              </FormikProvider>
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferSelectionDuplication
