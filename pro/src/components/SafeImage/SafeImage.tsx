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
  // https://gtmetrix.com/avoid-empty-src-or-href.html
  const sanitizedSrc = src.trim() || undefined

  const [error, setError] = useState(false)
  const previousSanitizedSrc = usePrevious(sanitizedSrc)

  useEffect(() => {
    if (sanitizedSrc !== previousSanitizedSrc) {
      setError(false)
    }
  }, [sanitizedSrc, previousSanitizedSrc])

  if (error) {
    return placeholder
  }

  return (
    <img
      className={className}
      src={sanitizedSrc}
      alt={alt}
      onError={() => setError(true)}
      data-testid={testId}
    />
  )
}
