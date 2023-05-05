import useNotification from 'hooks/useNotification'

import postCollectiveOfferImageAdapter from '../adapters/postCollectiveOfferImageAdapter'
import { IOfferEducationalFormValues } from '../types'

export interface PostCollectiveOfferImageProps {
  initialValues: IOfferEducationalFormValues
  notify: ReturnType<typeof useNotification>
  payload: { id: string }
}

export const postCollectiveOfferImage = async ({
  initialValues,
  notify,
  payload,
}: PostCollectiveOfferImageProps) => {
  const { imageUrl, imageCredit } = initialValues
  const imageErrorMessage = "Impossible de dupliquer l'image"
  /* istanbul ignore next: DEBT to fix */
  if (imageUrl) {
    const imageResponse = await fetch(imageUrl)
    if (!imageResponse.ok) {
      return notify.error(imageErrorMessage)
    }
    const contentType = imageResponse.headers.get('content-type')
    const blob = await imageResponse.blob()
    if (!blob) {
      return notify.error(imageErrorMessage)
    }
    /* istanbul ignore next: DEBT to fix */
    const imageFile = new File([blob], '', { type: contentType ?? '' })
    await postCollectiveOfferImageAdapter({
      offerId: payload.id,
      imageFile: imageFile,
      /* istanbul ignore next: DEBT to fix */
      credit: imageCredit ?? '',
      cropParams: { x: 0, y: 0, width: 1, height: 1 },
    })
  }
}
