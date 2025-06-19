import { useState } from 'react'

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
