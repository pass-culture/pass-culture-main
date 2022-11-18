import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  isCollectiveOffer,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import patchCollectiveOfferAdapter from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import postCollectiveOfferAdapter from 'core/OfferEducational/adapters/postCollectiveOfferAdapter'
import postCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferImageAdapter'
import { IOfferCollectiveImage } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

interface CollectiveOfferCreationProps {
  offer?: CollectiveOffer
  setOffer: (offer: CollectiveOffer) => void
}

const CollectiveOfferCreation = ({
  offer,
  setOffer,
}: CollectiveOfferCreationProps): JSX.Element => {
  const history = useHistory()
  const location = useLocation()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()
  const [imageOffer, setImageOffer] = useState<IOfferCollectiveImage | null>(
    offer !== undefined
      ? { url: offer.imageUrl, credit: offer.imageCredit }
      : null
  )
  const [imageToUpload, setImageToUpload] = useState<IOnImageUploadArgs | null>(
    null
  )

  const onImageUpload = async (image: IOnImageUploadArgs) => {
    setImageToUpload(image)
    setImageOffer({ url: image.imageCroppedDataUrl, credit: image.credit })
  }

  const onImageDelete = async () => {
    setImageToUpload(null)
    setImageOffer(null)
  }

  const createOrPatchDraftOffer = async (
    offerValues: IOfferEducationalFormValues
  ) => {
    const isCreatingOffer = offer !== undefined
    const adapter = isCreatingOffer
      ? () =>
          patchCollectiveOfferAdapter({
            offer: offerValues,
            initialValues,
            offerId: offer.id,
          })
      : () => postCollectiveOfferAdapter({ offer: offerValues })

    const { payload, isOk, message } = await adapter()

    if (!isOk) {
      return notify.error(message)
    }

    if (offer && isCollectiveOffer(payload)) {
      setOffer(payload)
    }
    const offerId = offer?.id ?? payload.id

    if (imageToUpload !== null) {
      const imageResponse = await postCollectiveOfferImageAdapter({
        offerId,
        imageFile: imageToUpload?.imageFile,
        credit: imageToUpload?.credit,
        cropParams: imageToUpload?.cropParams,
      })
      if (!imageResponse.isOk) {
        return notify.error(message)
      }
      setImageOffer({
        url: imageResponse.payload.imageUrl,
        credit: imageToUpload?.credit,
      })
    } else {
      if (!isCreatingOffer) {
        // TODO delete image
      }
    }

    history.push(`/offre/${payload.id}/collectif/stocks`)
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const result = await getCollectiveOfferFormDataApdater({
          offererId,
          offer,
        })

        if (!result.isOk) {
          notify.error(result.message)
        }

        const { categories, offerers, domains, initialValues } = result.payload

        setScreenProps({
          categories: categories,
          userOfferers: offerers,
          domainsOptions: domains,
        })

        setInitialValues(values =>
          setInitialFormValues(
            { ...values, ...initialValues },
            offerers,
            initialValues.offererId ?? offererId,
            initialValues.venueId ?? venueId
          )
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return isReady && screenProps ? (
    <>
      <OfferEducationalScreen
        {...screenProps}
        getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
        initialValues={initialValues}
        mode={Mode.CREATION}
        onSubmit={createOrPatchDraftOffer}
        isTemplate={false}
        imageOffer={imageOffer}
        onImageDelete={onImageDelete}
        onImageUpload={onImageUpload}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </>
  ) : (
    <Spinner />
  )
}

export default CollectiveOfferCreation
