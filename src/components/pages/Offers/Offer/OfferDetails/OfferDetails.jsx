/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'

import useNotification from 'components/hooks/useNotification'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Spinner from 'components/layout/Spinner'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { DEFAULT_FORM_VALUES } from 'components/pages/Offers/Offer/OfferDetails/OfferForm/_constants'
import OfferCreation from 'components/pages/Offers/Offer/OfferDetails/OfferForm/OfferCreation'
import OfferEditionContainer from 'components/pages/Offers/Offer/OfferDetails/OfferForm/OfferEditionContainer'
import OfferPreview from 'components/pages/Offers/Offer/OfferDetails/OfferPreview/OfferPreview'
import OfferStatusBanner from 'components/pages/Offers/Offer/OfferDetails/OfferStatusBanner/OfferStatusBanner'
import OfferThumbnail from 'components/pages/Offers/Offer/OfferDetails/OfferThumbnail/OfferThumbnail'
import OfferPreviewLink from 'components/pages/Offers/Offer/OfferPreviewLink/OfferPreviewLink'
import * as pcapi from 'repository/pcapi/pcapi'
import { loadCategories } from 'store/offers/thunks'

import { queryParamsFromOfferer } from '../../utils/queryParamsFromOfferer'


const OfferDetails = ({
  history,
  isUserAdmin,
  location,
  offer,
  reloadOffer,
  trackCreateOffer,
  trackEditOffer,
  userEmail,
}) => {
  const dispatch = useDispatch()
  const initialValues = {}
  const queryParams = queryParamsFromOfferer(location)

  if (queryParams.structure !== '') {
    initialValues.offererId = queryParams.structure
  }

  if (queryParams.lieu !== '') {
    initialValues.venueId = queryParams.lieu
  }

  const formInitialValues = useRef(initialValues)
  const [formValues, setFormValues] = useState({})
  const [offerSubCategory, setOfferSubCategory] = useState({})
  const [formErrors, setFormErrors] = useState({})
  const [showThumbnailForm, setShowThumbnailForm] = useState(false)
  const [thumbnailInfo, setThumbnailInfo] = useState({})
  const [thumbnailError, setThumbnailError] = useState(false)
  const { categories, subCategories } = useSelector(state => state.offers.categories)
  const [isLoading, setIsLoading] = useState(!(categories && subCategories))

  const notification = useNotification()
  const showErrorNotification = useCallback(
    () => notification.error('Une ou plusieurs erreurs sont présentes dans le formulaire')
    , [notification])

  useEffect(() => {
    offer?.id && reloadOffer()
  }, [offer?.id, reloadOffer])

  useEffect(() => {
    formValues.subcategoryId && setShowThumbnailForm(formValues.subcategoryId !== DEFAULT_FORM_VALUES.subcategoryId)
  }, [setShowThumbnailForm, formValues.subcategoryId])

  useEffect(() => {
    dispatch(loadCategories())
  }, [dispatch])

  useEffect(() => {
    if (categories && subCategories) {
      setIsLoading(false)
    }
  }, [categories, subCategories])

  const postThumbnail = useCallback(
    async (offerId, thumbnailInfo) => {
      const offerThumbnailHasBeenUpdated = Object.values(thumbnailInfo).length > 0
      if (offerThumbnailHasBeenUpdated) {
        const { credit, thumbnail, croppingRect, thumbUrl } = thumbnailInfo

        try {
          await pcapi.postThumbnail(
            offerId,
            credit,
            thumbnail,
            thumbUrl,
            croppingRect?.x,
            croppingRect?.y,
            croppingRect?.height
          )
        } catch (error) {
          setThumbnailError(true)
          showErrorNotification()

          throw error
        }
      }
    },
    [showErrorNotification]
  )

  const handleSubmitOffer = useCallback(
    async offerValues => {
      try {
        if (offer) {
          await pcapi.updateOffer(offer.id, offerValues)
          trackEditOffer(offer.id)
          notification.success('Votre offre a bien été modifiée')
          reloadOffer()
          setFormErrors({})
        } else {
          const response = await pcapi.createOffer(offerValues)
          const createdOfferId = response.id
          trackCreateOffer(createdOfferId)
          await postThumbnail(createdOfferId, thumbnailInfo)

          let queryString = ''

          if (formInitialValues.current.offererId !== undefined) {
            queryString = `?structure=${formInitialValues.current.offererId}`
          }

          if (formInitialValues.current.venueId !== undefined) {
            queryString += `&lieu=${formInitialValues.current.venueId}`
          }

          history.push(`/offres/${createdOfferId}/stocks${queryString}`)
          return Promise.resolve()
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
          return Promise.resolve()
        }
      }
    },
    [
      history,
      offer,
      postThumbnail,
      reloadOffer,
      notification,
      showErrorNotification,
      thumbnailInfo,
      trackEditOffer,
      trackCreateOffer,
    ]
  )

  const offerStatus = offer?.status
  const isDisabled = offerStatus ? isOfferDisabled(offerStatus) : false

  if (isLoading) {
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

      <div className={Object.entries(formValues).length !== 0 ? 'sidebar-container' : ''}>
        <div className="content">
          {offer ? (
            <>
              {isDisabled && <OfferStatusBanner status={offerStatus} />}
              <OfferEditionContainer
                categories={categories}
                formValues={formValues}
                isDisabled={isDisabled}
                isUserAdmin={isUserAdmin}
                offer={offer}
                onSubmit={handleSubmitOffer}
                setFormValues={setFormValues}
                setPreviewOfferCategory={setOfferSubCategory}
                showErrorNotification={showErrorNotification}
                subCategories={subCategories}
                submitErrors={formErrors}
                userEmail={userEmail}
              />
            </>
          ) : (
            <OfferCreation
              categories={categories}
              formValues={formValues}
              initialValues={formInitialValues.current}
              isUserAdmin={isUserAdmin}
              onSubmit={handleSubmitOffer}
              setFormValues={setFormValues}
              setPreviewOfferCategory={setOfferSubCategory}
              showErrorNotification={showErrorNotification}
              subCategories={subCategories}
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
                thumbnailError={thumbnailError}
                url={offer?.thumbUrl}
              />
              <OfferPreview
                formValues={formValues}
                offerSubCategory={offerSubCategory}
              />
            </div>
            {offer ? (
              <OfferPreviewLink
                nonHumanizedOfferId={offer.nonHumanizedId}
                offerId={offer.id}
              />
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
}

OfferDetails.propTypes = {
  history: PropTypes.shape().isRequired,
  isUserAdmin: PropTypes.bool.isRequired,
  location: PropTypes.shape().isRequired,
  offer: PropTypes.shape(),
  reloadOffer: PropTypes.func,
  trackCreateOffer: PropTypes.func.isRequired,
  trackEditOffer: PropTypes.func.isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default OfferDetails
