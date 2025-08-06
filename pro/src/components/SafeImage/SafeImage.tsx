import { useEffect, useState } from 'react'

import { usePrevious } from '@/commons/hooks/usePrevious'

type SafeImageProps = {
  src: string
  alt: string
  placeholder: React.ReactNode
  className?: string
  testId?: string
}

export function SafeImage({
  src,
  alt,
  className,
  testId,
  placeholder,
}: SafeImageProps) {
  const [error, setError] = useState(false)
  const previousSrc = usePrevious(src)

  useEffect(() => {
    if (src !== previousSrc) {
      setError(false)
    }
  }, [src, previousSrc])

  if (error) {
    return placeholder
  }

  return (
    <img
      className={className}
      src={src}
      alt={alt}
      onError={() => setError(true)}
      data-testid={testId}
    />
  )
}
