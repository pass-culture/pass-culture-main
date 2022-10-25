import PropTypes from 'prop-types'
import React, {
  Fragment,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { useSelector } from 'react-redux'
import { useHistory, useLocation } from 'react-router-dom'
import { v4 as generateRandomUuid } from 'uuid'

import { api } from 'apiClient/api'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import OfferStatusBanner from 'components/pages/Offers/Offer/OfferDetails/OfferStatusBanner/OfferStatusBanner'
import {
  createEventStockPayload,
  formatAndSortStocks,
  validateCreatedStock,
  validateUpdatedStock,
} from 'components/pages/Offers/Offer/Stocks/StockItem/domain'
import StockItem from 'components/pages/Offers/Offer/Stocks/StockItem/StockItem'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ReactComponent as AddStockSvg } from 'icons/ico-plus.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { SynchronizedProviderInformation } from 'screens/OfferIndividual/SynchronisedProviderInfos'
import {
  searchFiltersSelector,
  searchPageNumberSelector,
} from 'store/offers/selectors'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'

import { FormActions } from './FormActions'

const EMPTY_STRING_VALUE = ''

const EventStocks = ({ offer, reloadOffer, isCompletingDraft }) => {
  const offerId = offer.id
  const [isLoading, setIsLoading] = useState(true)
  const [isSendingStocksOfferCreation, setIsSendingStocksOfferCreation] =
    useState(false)
  const [stocks, setStocks] = useState([])
  const isOfferSynchronized = Boolean(offer.lastProvider)
  const [formErrors, setFormErrors] = useState({})
  const isOfferDraft = offer.status === OFFER_STATUS_DRAFT
  const { logEvent } = useAnalytics()
  const history = useHistory()
  const location = useLocation()
  const notification = useNotification()
  const isDraftEnabled = useActiveFeature('OFFER_DRAFT_ENABLED')

  /* istanbul ignore next: DEBT, TO FIX */
  const summaryStepUrl = isOfferDraft
    ? isCompletingDraft
      ? `/offre/${offer.id}/individuel/brouillon/recapitulatif`
      : `/offre/${offer.id}/individuel/creation/recapitulatif`
    : `/offre/${offer.id}/individuel/recapitulatif`
  const offersSearchFilters = useSelector(searchFiltersSelector)
  const offersPageNumber = useSelector(searchPageNumberSelector)
  const loadStocks = useCallback(
    async (keepCreationStocks = false) => {
      return api.getStocks(offerId).then(receivedStocks => {
        setStocks(oldStocks => {
          const stocksOnCreation = keepCreationStocks
            ? oldStocks.filter(stock => !stock.id)
            : []
          return [
            ...stocksOnCreation,
            ...formatAndSortStocks(
              receivedStocks.stocks,
              offer.venue.departementCode
            ),
          ]
        })
        setIsLoading(false)
      })
    },
    [offerId, offer.venue.departementCode]
  )

  const onDelete = useCallback(() => {
    reloadOffer()
    loadStocks(true)
  }, [loadStocks, reloadOffer])

  useEffect(() => {
    loadStocks()
  }, [loadStocks])

  useEffect(() => {
    if (Object.values(formErrors).length > 0) {
      notification.error(
        'Une ou plusieurs erreurs sont présentes dans le formulaire.'
      )
    }
  }, [formErrors])

  const addNewStock = useCallback(() => {
    const newStock = {
      key: generateRandomUuid(),
      price: EMPTY_STRING_VALUE,
      quantity: null,
      bookingLimitDatetime: null,
      beginningDatetime: null,
    }

    setStocks(currentStocks => [newStock, ...currentStocks])
  }, [])

  const removeStockInCreation = useCallback(
    key =>
      setStocks(currentStocks =>
        currentStocks.filter(stock => stock.key !== key)
      ),
    []
  )

  const existingStocks = useMemo(
    () => stocks.filter(stock => stock.id !== undefined),
    [stocks]
  )
  const stocksInCreation = useMemo(
    () => stocks.filter(stock => stock.id === undefined),
    [stocks]
  )

  const updateStock = useCallback(updatedStockValues => {
    setStocks(currentStocks => {
      const stockToUpdateIndex = currentStocks.findIndex(
        currentStock => currentStock.key === updatedStockValues.key
      )
      const updatedStock = {
        ...currentStocks[stockToUpdateIndex],
        ...updatedStockValues,
        updated: true,
      }
      let newStocks = [...currentStocks]
      newStocks.splice(stockToUpdateIndex, 1, updatedStock)
      return newStocks
    })
  }, [])

  const areValid = (stocks, isEvent) => {
    const stocksErrors = stocks.reduce((stocksErrors, stock) => {
      const isNewStock = stock.id === undefined
      const stockErrors = isNewStock
        ? validateCreatedStock(stock, isEvent)
        : validateUpdatedStock(stock, isEvent)
      const stockHasErrors = Object.keys(stockErrors).length > 0
      return stockHasErrors
        ? { ...stocksErrors, [stock.key]: stockErrors }
        : stocksErrors
    }, {})

    const hasErrors = Object.values(stocksErrors).length > 0

    if (hasErrors) {
      const formErrors = {
        global: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
        ...stocksErrors,
      }
      setFormErrors(formErrors)
    } else {
      setFormErrors({})
    }

    return !hasErrors
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const onCancelClick = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.STOCKS,
      to: isOfferDraft
        ? OfferBreadcrumbStep.DETAILS
        : OFFER_FORM_NAVIGATION_OUT.OFFERS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: !isOfferDraft,
      isDraft: isOfferDraft,
      offerId: offer.id,
    })
  }

  const submitDraft = e => submitStocks(e, true)

  const submitStocks = useCallback(
    (e, isSavingDraft = false) => {
      e.preventDefault()
      const updatedStocks = existingStocks.filter(stock => stock.updated)
      if (areValid([...stocksInCreation, ...updatedStocks], offer.isEvent)) {
        setIsSendingStocksOfferCreation(true)

        const stocksToCreate = stocksInCreation.map(stockInCreation =>
          createEventStockPayload(stockInCreation, offer.venue.departementCode)
        )
        const stocksToUpdate = updatedStocks.map(updatedStock => {
          const payload = createEventStockPayload(
            updatedStock,
            offer.venue.departementCode
          )
          payload.id = updatedStock.id
          return payload
        })
        api
          .upsertStocks({
            humanizedOfferId: offer.id,
            stocks: [
              ...stocksToCreate,
              ...stocksToUpdate.map(stock => {
                const apiStockEdition = { ...stock }
                apiStockEdition.humanizedId = apiStockEdition.id
                delete apiStockEdition.id
                return apiStockEdition
              }),
            ],
          })
          .then(async () => {
            const queryParams = queryParamsFromOfferer(location)
            let queryString = ''

            /* istanbul ignore next: DEBT, TO FIX */
            if (queryParams.structure !== '') {
              queryString = `?structure=${queryParams.structure}`
            }

            /* istanbul ignore next: DEBT, TO FIX */
            if (queryParams.lieu !== '') {
              queryString += `&lieu=${queryParams.lieu}`
            }
            if (isOfferDraft) {
              await reloadOffer(true)

              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OfferBreadcrumbStep.STOCKS,
                to: isSavingDraft
                  ? OfferBreadcrumbStep.STOCKS
                  : OfferBreadcrumbStep.SUMMARY,
                used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
                isEdition: false,
                isDraft: true,
                offerId: offer.id,
              })
              if (isDraftEnabled)
                notification.success(
                  'Brouillon sauvegardé dans la liste des offres'
                )
            } else {
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OfferBreadcrumbStep.STOCKS,
                to: OfferBreadcrumbStep.SUMMARY,
                used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
                isEdition: true,
                isDraft: false,
                offerId: offer.id,
              })
              await loadStocks()
              await reloadOffer()
              notification.success(
                'Vos modifications ont bien été enregistrées'
              )
            }
            if (!isSavingDraft) history.push(`${summaryStepUrl}${queryString}`)
          })
          .catch(() => {
            notification.error(
              'Une ou plusieurs erreurs sont présentes dans le formulaire.'
            )
          })
          .finally(() => setIsSendingStocksOfferCreation(false))
      }
    },
    [
      existingStocks,
      history,
      location,
      stocksInCreation,
      offer.id,
      offer.isEducational,
      offer.isEvent,
      isOfferDraft,
      offer.venue.departementCode,
      loadStocks,
      reloadOffer,
    ]
  )

  if (isLoading) {
    return null
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const hasNoStock = stocks.length === 0
  const hasAtLeastOneStock = stocks.length > 0
  /* istanbul ignore next: DEBT, TO FIX */
  const cancelUrl = isOfferDraft
    ? isCompletingDraft
      ? `/offre/${offerId}/individuel/brouillon`
      : `/offre/${offerId}/individuel/creation`
    : computeOffersUrl(offersSearchFilters, offersPageNumber)
  let providerName = offer.lastProvider?.name || null

  return (
    <div className="stocks-page">
      <PageTitle title="Vos stocks" />
      {(isDisabled || providerName !== null) && (
        <div className="banners">
          {isDisabled && (
            <div className="banner">
              <OfferStatusBanner status={offer.status} />
            </div>
          )}
          {providerName !== null && (
            <div className="banner">
              <SynchronizedProviderInformation providerName={providerName} />
            </div>
          )}
        </div>
      )}

      <h3 className="section-title">Stocks et prix</h3>

      <div className="cancellation-information">
        Les utilisateurs ont un délai de 48h pour annuler leur réservation mais
        ne peuvent pas le faire moins de 48h avant le début de l’évènement. Si
        la date limite de réservation n’est pas encore passée, la place est
        alors automatiquement remise en vente.
      </div>
      {hasNoStock ? (
        <Button
          className="add-first-stock-button"
          disabled={isDisabled}
          onClick={addNewStock}
          Icon={AddStockSvg}
        >
          Ajouter une date
        </Button>
      ) : (
        <Fragment>
          <Button
            disabled={isDisabled || isOfferSynchronized}
            onClick={addNewStock}
            Icon={AddStockSvg}
            variant={ButtonVariant.TERNARY}
          >
            Ajouter une date
          </Button>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Horaire</th>
                <th>Prix</th>
                <th>Date limite de réservation</th>
                <th>Quantité</th>
                {(stocksInCreation.length === 0 || existingStocks.length > 0) &&
                  !isCompletingDraft && (
                    <Fragment>
                      <th>Stock restant</th>
                      <th>Réservations</th>
                    </Fragment>
                  )}
                <th />
              </tr>
            </thead>
            <tbody>
              {stocksInCreation.map(stockInCreation => (
                <StockItem
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stockInCreation.key]}
                  initialStock={stockInCreation}
                  isDigital={offer.isDigital}
                  isEvent
                  isNewStock
                  key={stockInCreation.key}
                  onChange={updateStock}
                  onDelete={onDelete}
                  removeStockInCreation={removeStockInCreation}
                />
              ))}

              {existingStocks.map(stock => (
                <StockItem
                  departmentCode={offer.venue.departementCode}
                  errors={formErrors[stock.key]}
                  initialStock={stock}
                  isDigital={offer.isDigital}
                  isDisabled={isDisabled}
                  isEvent
                  isDraft={isCompletingDraft}
                  key={stock.id}
                  lastProvider={offer.lastProvider}
                  onChange={updateStock}
                  onDelete={onDelete}
                />
              ))}
            </tbody>
          </table>
        </Fragment>
      )}
      {(isOfferDraft || hasAtLeastOneStock) && (
        <Fragment>
          <div className="interval cover" />
          <div className="interval shadow" />
          <section className="actions-section">
            <FormActions
              cancelUrl={cancelUrl}
              canSubmit={!(isDisabled || hasNoStock)}
              isDraft={isOfferDraft}
              isSubmiting={isSendingStocksOfferCreation}
              onSubmit={submitStocks}
              onSubmitDraft={submitDraft}
              onCancelClick={onCancelClick}
            />
          </section>
        </Fragment>
      )}
    </div>
  )
}

EventStocks.propTypes = {
  offer: PropTypes.shape().isRequired,
  reloadOffer: PropTypes.func.isRequired,
}

export default EventStocks
