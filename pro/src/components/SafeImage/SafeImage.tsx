import { useEffect, useId, useState } from 'react'

import { usePrevious } from '@/commons/hooks/usePrevious'

import styles from '../SafeImage/ImagePlaceholder/ImagePlaceholder.module.scss'

type SafeImageProps = {
  src: string
  alt: string
  placeholder: React.ReactNode
  className?: string
  testId?: string
  ariaDescribedBy?: string
  credit?: string
}

export function SafeImage({
  src,
  alt,
  className,
  testId,
  placeholder,
  ariaDescribedBy,
  credit,
}: Readonly<SafeImageProps>) {
  // https://gtmetrix.com/avoid-empty-src-or-href.html
  const sanitizedSrc = src.trim() || undefined
  const imageCreditId = useId()

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
    <figure>
      <img
        className={className}
        src={sanitizedSrc}
        alt={alt}
        aria-describedby={[ariaDescribedBy, imageCreditId].join(' ')}
        onError={() => setError(true)}
        data-testid={testId}
      />
      {credit ? (
        <figcaption id={imageCreditId}>
          <p className={styles['image-credit-text']}>Crédit image : {credit}</p>
        </figcaption>
      ) : null}
    </figure>
  )
}
