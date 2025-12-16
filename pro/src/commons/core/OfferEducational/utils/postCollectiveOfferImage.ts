import { api } from '@/apiClient/api'
import type { useSnackBar } from '@/commons/hooks/useSnackBar'

import type { OfferEducationalFormValues } from '../types'

interface PostCollectiveOfferImageProps {
  initialValues: OfferEducationalFormValues
  snackBar: ReturnType<typeof useSnackBar>
  id: number
}

export const postCollectiveOfferImage = async ({
  initialValues,
  snackBar,
  id,
}: PostCollectiveOfferImageProps) => {
  const { imageUrl, imageCredit } = initialValues
  const imageErrorMessage = 'Impossible de dupliquer l’image'
  /* istanbul ignore next: DEBT to fix */
  if (imageUrl) {
    try {
      const imageResponse = await fetch(imageUrl)
      if (!imageResponse.ok) {
        return snackBar.error(imageErrorMessage)
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
    } catch {
      snackBar.error('Impossible de récupérer votre image')
    }
  }
}
