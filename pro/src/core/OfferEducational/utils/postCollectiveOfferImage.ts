import { api } from 'apiClient/api'
import { useNotification } from 'hooks/useNotification'

import { OfferEducationalFormValues } from '../types'

interface PostCollectiveOfferImageProps {
  initialValues: OfferEducationalFormValues
  notify: ReturnType<typeof useNotification>
  id: number
}

export const postCollectiveOfferImage = async ({
  initialValues,
  notify,
  id,
}: PostCollectiveOfferImageProps) => {
  const { imageUrl, imageCredit } = initialValues
  const imageErrorMessage = 'Impossible de dupliquer l’image'
  /* istanbul ignore next: DEBT to fix */
  if (imageUrl) {
    const imageResponse = await fetch(imageUrl)
    if (!imageResponse.ok) {
      return notify.error(imageErrorMessage)
    }
    const contentType = imageResponse.headers.get('content-type')
    const blob = await imageResponse.blob()

    /* istanbul ignore next: DEBT to fix */
    const imageFile = new File([blob], '', { type: contentType ?? '' })

    await api.attachOfferImage(id, {
      // TODO This TS error will be removed when spectree is updated to the latest
      // version (dependant on Flask update) which will include files in the generated schema
      // @ts-expect-error
      thumb: imageFile,
      credit: imageCredit ?? '',
      croppingRectHeight: 1,
      croppingRectWidth: 1,
      croppingRectX: 0,
      croppingRectY: 0,
    })
  }
}
