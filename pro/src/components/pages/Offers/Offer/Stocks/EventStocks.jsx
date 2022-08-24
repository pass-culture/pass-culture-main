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

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import SynchronizedProviderInformation from 'components/pages/Offers/Offer/OfferDetails/OfferForm/SynchronisedProviderInfos'
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
} from 'core/FirebaseEvents/constants'
import { OFFER_STATUS_DRAFT } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils'
import { ReactComponent as AddStockSvg } from 'icons/ico-plus.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import * as pcapi from 'repository/pcapi/pcapi'

import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'

import { FormActions } from './FormActions'

const EMPTY_STRING_VALUE = ''

const EventStocks = ({
  offer,
  showErrorNotification,
  showSuccessNotification,
  reloadOffer,
}) => {
  const offerId = offer.id
  const [isLoading, setIsLoading] = useState(true)
  const [isSendingStocksOfferCreation, setIsSendingStocksOfferCreation] =
    useState(false)
  const [stocks, setStocks] = useState([])
  const isOfferSynchronized = Boolean(offer.lastProvider)
  const [formErrors, setFormErrors] = useState({})
  const isOfferDraft = offer.status === OFFER_STATUS_DRAFT
  const { logEvent } = useAnalytics()
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')
  const history = useHistory()
  const location = useLocation()
  const summaryStepUrl = isOfferDraft
    ? `/offre/${offer.id}/individuel/creation/recapitulatif`
    : `/offre/${offer.id}/individuel/recapitulatif`
  const offersSearchFilters = useSelector(state => state.offers.searchFilters)
  const offersPageNumber = useSelector(state => state.offers.pageNumber)
  const loadStocks = useCallback(
    (keepCreationStocks = false) => {
      return pcapi.loadStocks(offerId).then(receivedStocks => {
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
      showErrorNotification()
    }
  }, [formErrors, showErrorNotification])

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

  const onCancelClick = () => {
    if (isOfferDraft && !useSummaryPage) return
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.STOCKS,
      to: OfferBreadcrumbStep.DETAILS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: !isOfferDraft,
    })
  }

  const submitStocks = useCallback(
    e => {
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
        pcapi
          .bulkCreateOrEditStock(offer.id, [
            ...stocksToCreate,
            ...stocksToUpdate,
          ])
          .then(async () => {
            const queryParams = queryParamsFromOfferer(location)
            let queryString = ''

            if (queryParams.structure !== '') {
              queryString = `?structure=${queryParams.structure}`
            }

            if (queryParams.lieu !== '') {
              queryString += `&lieu=${queryParams.lieu}`
            }
            if (isOfferDraft) {
              await reloadOffer(true)
              if (!useSummaryPage) {
                await showSuccessNotification(
                  'Votre offre a bien été créée et vos stocks sauvegardés.'
                )
              }

              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OfferBreadcrumbStep.STOCKS,
                to: OfferBreadcrumbStep.SUMMARY,
                used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
                isEdition: !isOfferDraft,
              })
              history.push(
                useSummaryPage
                  ? `${summaryStepUrl}${queryString}`
                  : `/offre/${offer.id}/individuel/creation/confirmation${queryString}`
              )
            } else {
              await loadStocks()
              await reloadOffer()
              await showSuccessNotification(
                'Vos modifications ont bien été enregistrées'
              )
              setIsSendingStocksOfferCreation(false)
              if (useSummaryPage) {
                history.push(`${summaryStepUrl}${queryString}`)
              }
            }
          })
          .catch(() => {
            showErrorNotification()
            setIsSendingStocksOfferCreation(false)
          })
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
      showSuccessNotification,
      showErrorNotification,
    ]
  )

  if (isLoading) {
    return null
  }

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const hasNoStock = stocks.length === 0
  const hasAtLeastOneStock = stocks.length > 0
  const cancelUrl = isOfferDraft
    ? useSummaryPage
      ? `/offre/${offerId}/individuel/creation`
      : undefined
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
        <button
          className="primary-button with-icon add-first-stock-button"
          disabled={isDisabled}
          onClick={addNewStock}
          type="button"
        >
          <AddStockSvg />
          Ajouter une date
        </button>
      ) : (
        <Fragment>
          <button
            className="tertiary-button with-icon"
            disabled={isDisabled || isOfferSynchronized}
            onClick={addNewStock}
            type="button"
          >
            <AddStockSvg />
            Ajouter une date
          </button>
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Horaire</th>
                <th>Prix</th>
                <th>Date limite de réservation</th>
                <th>Quantité</th>
                {(stocksInCreation.length === 0 ||
                  existingStocks.length > 0) && (
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
  showErrorNotification: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
}

export default EventStocks
