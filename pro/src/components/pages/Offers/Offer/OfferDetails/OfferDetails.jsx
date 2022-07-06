import * as pcapi from 'repository/pcapi/pcapi'

import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { DEFAULT_FORM_VALUES } from './_constants'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import OfferCreation from './OfferCreation'
import OfferEdition from './OfferEdition'
import OfferPreview from './OfferPreview'
import OfferStatusBanner from './OfferStatusBanner'
import OfferThumbnail from './OfferThumbnail'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import PropTypes from 'prop-types'
import Spinner from 'components/layout/Spinner'
import { computeInitialValuesFromOffer } from './utils'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useGetCategories } from 'core/Offers/adapters'
import useNotification from 'components/hooks/useNotification'

const OfferDetails = ({
  isCreatingOffer,
  isUserAdmin,
  offer,
  reloadOffer,
  userEmail,
}) => {
  const history = useHistory()
  const location = useLocation()

  const [formInitialValues, setFormInitialValues] = useState({})
  const [isReady, setIsReady] = useState(false)

  const [formErrors, setFormErrors] = useState({})
  const [offerPreviewData, setOfferPreviewData] = useState({})
  const [showThumbnailForm, setShowThumbnailForm] = useState(false)
  const [thumbnailInfo, setThumbnailInfo] = useState({})
  const [thumbnailError, setThumbnailError] = useState(false)
  const [thumbnailMsgError, setThumbnailMsgError] = useState('')
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

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
          await pcapi.updateOffer(offer.id, offerValues)
          if (!isCreatingOffer)
            notification.success('Votre offre a bien été modifiée')
          reloadOffer()
          setFormErrors({})
          setThumbnailError(false)
          setThumbnailMsgError('')
          if (useSummaryPage && isCreatingOffer) {
            return Promise.resolve(() => goToStockAndPrice(offer.id))
          }
        } else {
          const response = await pcapi.createOffer(offerValues)
          const createdOfferId = response.id
          await postThumbnail(createdOfferId, thumbnailInfo)

          if (Object.keys(thumbnailInfo).length === 0) {
            return Promise.resolve(() => goToStockAndPrice(createdOfferId))
          }
        }
      } catch (error) {
        if (error && 'errors' in error) {
          const mapApiErrorsToFormErrors = {
            venue: 'venueId',
          }
          let newFormErrors = {}
          let formFieldName
          for (let apiFieldName in error.errors) {
            formFieldName = apiFieldName
            if (apiFieldName in mapApiErrorsToFormErrors) {
              formFieldName = mapApiErrorsToFormErrors[apiFieldName]
            }
            newFormErrors[formFieldName] = error.errors[apiFieldName]
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
                isUserAdmin={isUserAdmin}
                offer={offer}
                isCreatingOffer={isCreatingOffer}
                onSubmit={handleSubmitOffer}
                setOfferPreviewData={setOfferPreviewData}
                showErrorNotification={showErrorNotification}
                subCategories={categoriesData.subCategories}
                submitErrors={formErrors}
                userEmail={userEmail}
              />
            </>
          ) : (
            <OfferCreation
              categories={categoriesData.categories}
              initialValues={formInitialValues}
              isUserAdmin={isUserAdmin}
              onSubmit={handleSubmitOffer}
              setOfferPreviewData={setOfferPreviewData}
              showErrorNotification={showErrorNotification}
              subCategories={categoriesData.subCategories}
              submitErrors={formErrors}
              userEmail={userEmail}
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
            {offer ? (
              <DisplayOfferInAppLink nonHumanizedId={offer.nonHumanizedId} />
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
  isUserAdmin: PropTypes.bool.isRequired,
  offer: PropTypes.shape(),
  reloadOffer: PropTypes.func,
  userEmail: PropTypes.string.isRequired,
  isCreatingOffer: PropTypes.bool,
}

export default OfferDetails
