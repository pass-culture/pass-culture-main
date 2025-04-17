import { useEffect, useState } from 'react'

import { getImageBitmap } from 'commons/utils/image'

export const useGetImageBitmap = (file?: File) => {
  const [width, setWidth] = useState<number>(0)
  const [height, setHeight] = useState<number>(0)

  useEffect(() => {
    const updateImageSize = async () => {
      if (file) {
        const data = await getImageBitmap(file)
        /* istanbul ignore next: DEBT, TO FIX */
        if (data) {
          setWidth(data.width)
          setHeight(data.height)
        }
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    updateImageSize()
  }, [file])

  if (!file) {
    return { width: 0, height: 0 }
  }

  return { width, height }
}
