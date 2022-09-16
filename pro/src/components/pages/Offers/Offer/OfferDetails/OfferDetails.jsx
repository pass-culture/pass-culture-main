import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import useAnalytics from 'components/hooks/useAnalytics'
import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { useGetCategories } from 'core/Offers/adapters'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import * as pcapi from 'repository/pcapi/pcapi'
import { ButtonVariant } from 'ui-kit/Button/types'

import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'

import { DEFAULT_FORM_VALUES } from './_constants'
import OfferCreation from './OfferCreation'
import OfferEdition from './OfferEdition'
import OfferPreview from './OfferPreview'
import OfferStatusBanner from './OfferStatusBanner'
import OfferThumbnail from './OfferThumbnail'
import { computeInitialValuesFromOffer } from './utils'

const OfferDetails = ({ isCreatingOffer, offer, reloadOffer }) => {
  const history = useHistory()
  const location = useLocation()
  const { currentUser } = useCurrentUser()

  const [formInitialValues, setFormInitialValues] = useState({})
  const [isReady, setIsReady] = useState(false)

  const [formErrors, setFormErrors] = useState({})
  const [offerPreviewData, setOfferPreviewData] = useState({})
  const [showThumbnailForm, setShowThumbnailForm] = useState(false)
  const [thumbnailInfo, setThumbnailInfo] = useState({})
  const [thumbnailError, setThumbnailError] = useState(false)
  const [thumbnailMsgError, setThumbnailMsgError] = useState('')
  const { logEvent } = useAnalytics()

  const {
    data: categoriesData,
    isLoading: isLoadingCategories,
    error: categoriesError,
  } = useGetCategories()

  useEffect(() => {
    if (!isLoadingCategories) {
      let initialValues = {}
      const queryParams = queryParamsFromOfferer(location)
      if (queryParams.structure !== '') {
        initialValues.offererId = queryParams.structure
      }
      if (queryParams.lieu !== '') {
        initialValues.venueId = queryParams.lieu
      }
      initialValues.isVirtualVenue = queryParams.numerique

      initialValues = {
        ...initialValues,
        ...computeInitialValuesFromOffer(offer, categoriesData.subCategories),
      }
      setFormInitialValues(initialValues)
      setIsReady(true)
    }
  }, [isLoadingCategories, categoriesData, offer])

  const notification = useNotification()
  const showErrorNotification = useCallback(
    () =>
      notification.error(
        'Une ou plusieurs erreurs sont présentes dans le formulaire'
      ),
    [notification]
  )

  useEffect(() => {
    offer?.id && reloadOffer()
  }, [offer?.id, reloadOffer])

  useEffect(() => {
    offerPreviewData.subcategoryId &&
      setShowThumbnailForm(
        offerPreviewData.subcategoryId !== DEFAULT_FORM_VALUES.subcategoryId
      )
  }, [setShowThumbnailForm, offerPreviewData.subcategoryId])

  const goToStockAndPrice = async offerId => {
    let queryString = ''

    if (formInitialValues.offererId !== undefined) {
      queryString = `?structure=${formInitialValues.offererId}`
    }

    if (formInitialValues.venueId !== undefined) {
      queryString += `&lieu=${formInitialValues.venueId}`
    }

    history.push(`/offre/${offerId}/individuel/creation/stocks${queryString}`)
  }

  const postThumbnail = useCallback(
    async (offerId, thumbnailInfo) => {
      const offerThumbnailHasBeenUpdated =
        Object.values(thumbnailInfo).length > 0
      if (offerThumbnailHasBeenUpdated) {
        const { credit, thumbnail, croppingRect, thumbUrl } = thumbnailInfo

        await pcapi
          .postThumbnail(
            offerId,
            credit,
            thumbnail,
            thumbUrl,
            croppingRect?.x,
            croppingRect?.y,
            croppingRect?.height,
            croppingRect?.width
          )
          .then(() => {
            setThumbnailError(false)
            setThumbnailMsgError('')

            if (!offer) {
              goToStockAndPrice(offerId)
            }
          })
          .catch(error => {
            setThumbnailInfo({})
            setThumbnailError(true)
            if (error.errors?.errors?.length > 0) {
              setThumbnailMsgError(error.errors.errors[0])
            }
            showErrorNotification()

            throw error
          })
      }
    },
    [showErrorNotification]
  )

  const handleSubmitOffer = useCallback(
    async offerValues => {
      try {
        if (offer) {
          await api.patchOffer(offer.id, offerValues)
          if (!isCreatingOffer)
            notification.success('Vos modifications ont bien été enregistrées')
          reloadOffer()
          setFormErrors({})
          setThumbnailError(false)
          setThumbnailMsgError('')
          if (isCreatingOffer) {
            return Promise.resolve(() => goToStockAndPrice(offer.id))
          } else {
            return Promise.resolve(() =>
              history.push(`/offre/${offer.id}/individuel/recapitulatif`)
            )
          }
        } else {
          const response = await api.postOffer(offerValues)
          const createdOfferId = response.id
          await postThumbnail(createdOfferId, thumbnailInfo)
          if (Object.keys(thumbnailInfo).length === 0) {
            return Promise.resolve(() => goToStockAndPrice(createdOfferId))
          }
        }
      } catch (error) {
        if (isErrorAPIError(error)) {
          const errors = getError(error)
          const mapApiErrorsToFormErrors = {
            venue: 'venueId',
          }
          let newFormErrors = {}
          let formFieldName
          for (let apiFieldName in errors) {
            formFieldName = apiFieldName
            if (apiFieldName in mapApiErrorsToFormErrors) {
              formFieldName = mapApiErrorsToFormErrors[apiFieldName]
            }
            newFormErrors[formFieldName] = errors[apiFieldName]
          }
          setFormErrors(newFormErrors)
          showErrorNotification()
        }
      }
      return Promise.resolve(null)
    },
    [
      history,
      offer,
      postThumbnail,
      reloadOffer,
      notification,
      showErrorNotification,
      thumbnailInfo,
    ]
  )

  const offerStatus = offer?.status
  const isDisabled = offerStatus ? isOfferDisabled(offerStatus) : false

  if (categoriesError) {
    notification.error(categoriesError)
    history.push('/offres/')
    return null
  }

  if (!isReady) {
    return (
      <>
        <PageTitle title="Détails de l'offre" />
        <Spinner />
      </>
    )
  }

  return (
    <>
      <PageTitle title="Détails de l'offre" />

      <div className="sidebar-container">
        <div className="content">
          {offer ? (
            <>
              {isDisabled && <OfferStatusBanner status={offerStatus} />}
              <OfferEdition
                categories={categoriesData.categories}
                initialValues={formInitialValues}
                isDisabled={isDisabled}
                isUserAdmin={currentUser.isAdmin}
                offer={offer}
                isCreatingOffer={isCreatingOffer}
                onSubmit={handleSubmitOffer}
                setOfferPreviewData={setOfferPreviewData}
                showErrorNotification={showErrorNotification}
                subCategories={categoriesData.subCategories}
                submitErrors={formErrors}
                userEmail={currentUser.email}
              />
            </>
          ) : (
            <OfferCreation
              categories={categoriesData.categories}
              initialValues={formInitialValues}
              isUserAdmin={currentUser.isAdmin}
              onSubmit={handleSubmitOffer}
              setOfferPreviewData={setOfferPreviewData}
              showErrorNotification={showErrorNotification}
              subCategories={categoriesData.subCategories}
              submitErrors={formErrors}
              userEmail={currentUser.email}
            />
          )}
        </div>

        {showThumbnailForm && (
          <div className="sidebar">
            <div className="sidebar-wrapper">
              <OfferThumbnail
                isDisabled={isDisabled}
                offerId={offer?.id}
                postThumbnail={postThumbnail}
                setThumbnailInfo={setThumbnailInfo}
                setThumbnailError={setThumbnailError}
                setThumbnailMsgError={setThumbnailMsgError}
                thumbnailError={thumbnailError}
                thumbnailMsgError={thumbnailMsgError}
                url={offer?.thumbUrl}
              />
              <OfferPreview offerPreviewData={offerPreviewData} />
            </div>
            {!isCreatingOffer ? (
              <div className="offer-details-offer-preview-app-link">
                <DisplayOfferInAppLink
                  nonHumanizedId={offer.nonHumanizedId}
                  tracking={{
                    isTracked: true,
                    trackingFunction: () =>
                      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                        from: OfferBreadcrumbStep.DETAILS,
                        to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
                        used: OFFER_FORM_NAVIGATION_MEDIUM.DETAILS_PREVIEW,
                        isEdition: true,
                      }),
                  }}
                  variant={ButtonVariant.SECONDARY}
                />
              </div>
            ) : null}
          </div>
        )}
      </div>
    </>
  )
}

OfferDetails.defaultProps = {
  offer: null,
  reloadOffer: null,
  isCreatingOffer: false,
}

OfferDetails.propTypes = {
  offer: PropTypes.shape(),
  reloadOffer: PropTypes.func,
  isCreatingOffer: PropTypes.bool,
}

export default OfferDetails
