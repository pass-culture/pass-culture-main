import { useEffect, useState } from 'react'

import { getImageBitmap } from 'utils/image'

export const useGetImageBitmap = (file: File) => {
  const [width, setWidth] = useState<number>(0)
  const [height, setHeight] = useState<number>(0)

  useEffect(() => {
    getImageBitmap(file).then(data => {
      if (data) {
        setWidth(data.width)
        setHeight(data.height)
      }
    })
  }, [])

  return { width, height }
}
