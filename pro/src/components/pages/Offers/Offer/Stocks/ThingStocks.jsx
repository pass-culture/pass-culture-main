import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { v4 as generateRandomUuid } from 'uuid'

import useOfferEditionURL from 'components/hooks/useOfferEditionURL'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import OfferStatusBanner from 'components/pages/Offers/Offer/OfferDetails/OfferStatusBanner/OfferStatusBanner'
import {
  createThingStockPayload,
  formatStock,
  validateCreatedStock,
  validateUpdatedStock,
} from 'components/pages/Offers/Offer/Stocks/StockItem/domain'
import StockItemContainer from 'components/pages/Offers/Offer/Stocks/StockItem/StockItemContainer'
import {
  LIVRE_PAPIER_SUBCATEGORY_ID,
  OFFER_STATUS_DRAFT,
} from 'components/pages/Offers/Offers/_constants'
import { ReactComponent as AddStockSvg } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { SubmitButton } from 'ui-kit'

import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'

import PriceErrorHTMLNotification from './PriceErrorHTMLNotification'

const EMPTY_STRING_VALUE = ''

const ThingStocks = ({
  history,
  location,
  offer,
  showErrorNotification,
  showSuccessNotification,
  showHtmlErrorNotification,
  reloadOffer,
  autoActivateDigitalBookings,
  areActivationCodesEnabled,
}) => {
  const offerId = offer.id
  const [isLoading, setIsLoading] = useState(true)
  const [enableSubmitButtonSpinner, setEnableSubmitButtonSpinner] =
    useState(false)
  const [formErrors, setFormErrors] = useState({})
  const isOfferDraft = offer.status === OFFER_STATUS_DRAFT
  const editionOfferLink = useOfferEditionURL(offer.isEducational, offerId)
  const [stock, setStock] = useState(null)
  const displayExpirationDatetime =
    stock && stock.activationCodesExpirationDatetime !== null
  const loadStocks = useCallback(() => {
    return pcapi.loadStocks(offerId).then(receivedStocks => {
      if (!receivedStocks.stocks.length) {
        setStock(null)
      } else {
        setStock(
          formatStock(receivedStocks.stocks[0], offer.venue.departementCode)
        )
      }
      setIsLoading(false)
    })
  }, [offerId, offer.venue.departementCode])

  useEffect(() => {
    loadStocks()
  }, [loadStocks])

  const onDelete = useCallback(() => {
    reloadOffer()
    loadStocks()
  }, [loadStocks, reloadOffer])

  useEffect(() => {
    if (Object.values(formErrors).length > 0) {
      if (formErrors.price300) {
        showHtmlErrorNotification(PriceErrorHTMLNotification())
      } else {
        showErrorNotification()
      }
    }
  }, [formErrors, showErrorNotification, showHtmlErrorNotification])

  const addNewStock = useCallback(() => {
    const newStock = {
      key: generateRandomUuid(),
      price: EMPTY_STRING_VALUE,
      quantity: null,
      bookingLimitDatetime: null,
      activationCodes: [],
      activationCodesExpirationDatetime: null,
    }
    setStock(newStock)
  }, [])

  const removeStockInCreation = useCallback(() => setStock(null), [])

  const updateStock = useCallback(updatedStockValues => {
    setStock(previousStock => ({
      ...previousStock,
      ...updatedStockValues,
      updated: true,
    }))
  }, [])

  const checkStockIsValid = (stock, isEvent, isEducational) => {
    const isNewStock = stock.id === undefined
    const stockErrors = isNewStock
      ? validateCreatedStock(stock, isEvent, isEducational)
      : validateUpdatedStock(stock, isEvent, isEducational)
    const stockHasErrors = Object.keys(stockErrors).length > 0

    if (stockHasErrors) {
      const formErrors = {
        global: 'Une ou plusieurs erreurs sont présentes dans le formulaire.',
        ...stockErrors,
      }
      setFormErrors(formErrors)
    } else {
      setFormErrors({})
    }

    return !stockHasErrors
  }

  const submitStocks = useCallback(() => {
    if (checkStockIsValid(stock, offer.isEvent, offer.isEducational)) {
      setEnableSubmitButtonSpinner(true)
      const stockToCreateOrEdit = {
        ...createThingStockPayload(stock, offer.venue.departementCode),
        id: stock.id,
      }
      const quantityOfActivationCodes = (stock.activationCodes || []).length
      pcapi
        .bulkCreateOrEditStock(offer.id, [stockToCreateOrEdit])
        .then(() => {
          if (isOfferDraft) {
            reloadOffer(true)
            if (quantityOfActivationCodes) {
              showSuccessNotification(
                `${quantityOfActivationCodes} ${
                  quantityOfActivationCodes > 1
                    ? ' Codes d’activation ont été ajoutés'
                    : ' Code d’activation a été ajouté'
                }`
              )
            } else {
              showSuccessNotification(
                'Votre offre a bien été créée et vos stocks sauvegardés.'
              )
            }

            const queryParams = queryParamsFromOfferer(location)
            let queryString = ''

            if (queryParams.structure !== '') {
              queryString = `?structure=${queryParams.structure}`
            }

            if (queryParams.lieu !== '') {
              queryString += `&lieu=${queryParams.lieu}`
            }

            history.push(
              `/offre/${offer.id}/individuel/confirmation${queryString}`
            )
          } else {
            loadStocks()
            reloadOffer()
            if (quantityOfActivationCodes) {
              showSuccessNotification(
                `${quantityOfActivationCodes} ${
                  quantityOfActivationCodes > 1
                    ? ' Codes d’activation ont été ajoutés'
                    : ' Code d’activation a été ajouté'
                }`
              )
            } else {
              showSuccessNotification('Vos stocks ont bien été sauvegardés.')
            }
          }
        })
        .catch(() => showErrorNotification())
        .finally(() => setEnableSubmitButtonSpinner(false))
    }
  }, [
    stock,
    history,
    location,
    offer.id,
    offer.isEducational,
    offer.isEvent,
    isOfferDraft,
    offer.venue.departementCode,
    loadStocks,
    reloadOffer,
    showSuccessNotification,
    showErrorNotification,
  ])

  if (isLoading) {
    return null
  }

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const hasNoStock = !stock
  const hasAStock = !hasNoStock
  const inCreateMode = hasNoStock || !stock.id
  return (
    <div className="stocks-page">
      <PageTitle title="Vos stocks" />

      {isDisabled && <OfferStatusBanner status={offer.status} />}

      <h3 className="section-title">Stock et prix</h3>

      <div className="cancellation-information">
        {(!offer.isDigital || !autoActivateDigitalBookings) &&
          `Les utilisateurs ont ${
            offer.subcategoryId === LIVRE_PAPIER_SUBCATEGORY_ID ? '10' : '30'
          } jours pour faire valider leur contremarque. Passé ce délai, la réservation est automatiquement annulée et l’offre remise en vente.`}
        {offer.isDigital &&
          autoActivateDigitalBookings &&
          'Les utilisateurs ont 30 jours pour annuler leurs réservations d’offres numériques. Dans le cas d’offres avec codes d’activation, les utilisateurs ne peuvent pas annuler leurs réservations d’offres numériques. Toute réservation est définitive et sera immédiatement validée.'}
      </div>
      {areActivationCodesEnabled && offer.isDigital && (
        <div className="activation-codes-information">
          Pour ajouter des codes d’activation, veuillez passer par le menu ···
          et choisir l’option correspondante.
        </div>
      )}
      {hasNoStock ? (
        <button
          className="primary-button with-icon add-first-stock-button"
          disabled={isDisabled}
          onClick={addNewStock}
          type="button"
        >
          <AddStockSvg />
          Ajouter un stock
        </button>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Prix</th>
              <th>Date limite de réservation</th>
              {displayExpirationDatetime && <th>Date limite de validité</th>}
              <th>Quantité</th>
              {!inCreateMode && (
                <Fragment>
                  <th>Stock restant</th>
                  <th>Réservations</th>
                </Fragment>
              )}
              <th />
            </tr>
          </thead>
          <tbody>
            {inCreateMode ? (
              <StockItemContainer
                departmentCode={offer.venue.departementCode}
                errors={formErrors}
                initialStock={stock}
                isDigital={offer.isDigital}
                isEvent={false}
                isNewStock
                key={stock.key}
                onChange={updateStock}
                onDelete={onDelete}
                removeStockInCreation={removeStockInCreation}
              />
            ) : (
              <StockItemContainer
                departmentCode={offer.venue.departementCode}
                errors={formErrors}
                initialStock={stock}
                isDigital={offer.isDigital}
                isDisabled={isDisabled}
                isEvent={false}
                key={stock.id}
                lastProvider={offer.lastProvider}
                onChange={updateStock}
                onDelete={onDelete}
              />
            )}
          </tbody>
        </table>
      )}
      {(isOfferDraft || hasAStock) && (
        <Fragment>
          <div className="interval cover" />
          <div className="interval shadow" />
          <section className="actions-section">
            {!isOfferDraft && (
              <Link className="secondary-link" to={editionOfferLink}>
                Annuler et quitter
              </Link>
            )}
            <SubmitButton
              disabled={isDisabled || hasNoStock}
              isLoading={enableSubmitButtonSpinner}
              onClick={submitStocks}
            >
              {isOfferDraft ? 'Valider et créer l’offre' : 'Enregistrer'}
            </SubmitButton>
          </section>
        </Fragment>
      )}
    </div>
  )
}

ThingStocks.propTypes = {
  areActivationCodesEnabled: PropTypes.bool.isRequired,
  autoActivateDigitalBookings: PropTypes.bool.isRequired,
  history: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  offer: PropTypes.shape().isRequired,
  reloadOffer: PropTypes.func.isRequired,
  showErrorNotification: PropTypes.func.isRequired,
  showHtmlErrorNotification: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
}

export default ThingStocks
