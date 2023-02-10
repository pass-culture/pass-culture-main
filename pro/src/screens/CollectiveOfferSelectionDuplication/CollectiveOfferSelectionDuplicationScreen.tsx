import cn from 'classnames'
import { Form, FormikProvider, useFormik } from 'formik'
import React, { useCallback, useEffect, useState } from 'react'
import { Link, useHistory } from 'react-router-dom'

import ActionsBarSticky from 'components/ActionsBarSticky'
import PageTitle from 'components/PageTitle/PageTitle'
import { createOfferFromTemplate } from 'core/OfferEducational'
import { computeOffersUrl, DEFAULT_SEARCH_FILTERS } from 'core/Offers'
import { Offer } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import { ReactComponent as SearchIco } from 'icons/search-ico.svg'
import { getFilteredCollectiveOffersAdapter } from 'pages/CollectiveOffers/adapters'
import {
  Button,
  RadioButton,
  SubmitButton,
  TextInput,
  Thumb,
  Title,
} from 'ui-kit'
import Icon from 'ui-kit/Icon/Icon'
import Titles from 'ui-kit/Titles/Titles'
import { pluralize } from 'utils/pluralize'

import styles from './CollectiveOfferSelectionDuplication.module.scss'

export interface CollectiveOfferSelectionDuplicationProps {
  offers: Offer[]
  isLoading: boolean
  showAll: boolean
  filterTemplateOfferByName: (offerName: string) => void
}

const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const [offers, setOffers] = useState<Offer[]>([])
  const [showAll, setShowAll] = useState(true)
  const notify = useNotification()
  const history = useHistory()
  const formik = useFormik({
    initialValues: { searchFilter: '', templateOfferId: '' },
    onSubmit: () => handleOnSubmit(),
  })
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')

  const filterTemplateOfferByName = useCallback(
    async (offerName: string) => {
      setIsLoading(true)
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        nameOrIsbn: offerName,
        collectiveOfferType: 'template',
        offererId: queryOffererId ?? 'all',
        venueId: queryVenueId ?? 'all',
      }
      const { isOk, message, payload } =
        await getFilteredCollectiveOffersAdapter(apiFilters)

      if (!isOk) {
        setIsLoading(false)
        return notify.error(message)
      }

      if (offerName.length < 1) {
        setShowAll(true)
      } else {
        setShowAll(false)
      }

      setOffers(payload.offers)
      setIsLoading(false)
    },
    [notify]
  )

  useEffect(() => {
    filterTemplateOfferByName(formik.initialValues.searchFilter)
  }, [formik.initialValues.searchFilter])

  const handleOnSubmit = () => {
    const templateOfferId = formik.values.templateOfferId
    if (templateOfferId === '') {
      return notify.error(
        'Vous devez séléctionner une offre vitrine à dupliquer'
      )
    }
    createOfferFromTemplate(history, notify, templateOfferId)
  }

  return (
    <div className="container">
      <PageTitle title="Créer une offre réservable" />
      <Titles title="Créer une offre réservable" />
      <Title as="h3" className="sub-title" level={4}>
        Séléctionner l’offre vitrine à dupliquer
      </Title>
      <FormikProvider value={formik}>
        <Form>
          <div className={styles['search-container']}>
            <TextInput
              label="Offre vitrine à dupliquer"
              isLabelHidden
              name="searchFilter"
              placeholder="Rechercher une offre vitrine"
            />
            <Button
              onClick={() =>
                filterTemplateOfferByName(formik.values.searchFilter)
              }
              isLoading={isLoading}
              className={styles['search-button']}
              aria-label="Button de recherche"
              Icon={SearchIco}
            >
              Rechercher
            </Button>
            <p className={styles['offer-info']}>
              {showAll
                ? 'Les dernières offres vitrines créées'
                : `${pluralize(offers.length, 'offre')} vitrine`}
            </p>
            {offers?.slice(0, 5).map(offer => (
              <div
                key={offer.id}
                className={cn(styles['offer-selection'], {
                  [styles['offer-selected']]:
                    formik.values.templateOfferId === offer.id,
                })}
              >
                <RadioButton
                  name="templateOfferId"
                  value={offer.id}
                  label={
                    <div className={styles['offer-selection-label']}>
                      <Thumb
                        url={offer.thumbUrl}
                        alt={offer.name}
                        className={styles['img-offer']}
                      />
                      <p className={styles['offer-title']}>
                        <strong>{offer.name}</strong>
                        {offer.venue.name}
                      </p>
                    </div>
                  }
                />
              </div>
            ))}
            {offers?.length < 1 && (
              <div className={styles['search-no-results']}>
                <Icon
                  alt="Illustration de recherche"
                  className={styles['search-no-results-icon']}
                  svg="ico-search-gray"
                />
                <p className={styles['search-no-results-text']}>
                  Aucune offre trouvée pour votre recherche
                </p>
              </div>
            )}
            <ActionsBarSticky>
              <ActionsBarSticky.Left>
                <Link className="secondary-link" to={computeOffersUrl({})}>
                  Annuler et quitter
                </Link>
              </ActionsBarSticky.Left>
              <ActionsBarSticky.Right>
                <SubmitButton className="primary-button" disabled={false}>
                  Étape suivante
                </SubmitButton>
              </ActionsBarSticky.Right>
            </ActionsBarSticky>
          </div>
        </Form>
      </FormikProvider>
    </div>
  )
}

export default CollectiveOfferSelectionDuplication
