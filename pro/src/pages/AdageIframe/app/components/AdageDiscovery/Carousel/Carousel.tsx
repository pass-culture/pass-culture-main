import cn from 'classnames'
import { createRef } from 'react'

import { useIsElementVisible } from '@/commons/hooks/useIsElementVisible'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullArrowLeftIcon from '@/icons/full-arrow-left.svg'
import fullArrowRightIcon from '@/icons/full-arrow-right.svg'

import { AdageSkeleton } from '../../Skeleton/AdageSkeleton'
import styles from './Carousel.module.scss'

type CarouselProps = {
  title?: JSX.Element
  elements: JSX.Element[]
  onLastCarouselElementVisible?: () => void
  loading?: boolean
  className?: string
  observableRef?: React.RefObject<HTMLDivElement> //  Reference for the  IntersectionObserver API
}

export function Carousel({
  title,
  elements,
  onLastCarouselElementVisible,
  loading,
  className,
  observableRef,
}: CarouselProps) {
  const listRef = createRef<HTMLUListElement>()
  const firstElementRef = createRef<HTMLLIElement>()
  const lastElementRef = createRef<HTMLLIElement>()

  const observerOptions = {
    threshold: 0.99,
    //  Only the list-item's visibility on the x-axis must be considered
    rootMargin: '100% 0px 100% 0px',
    root: observableRef?.current,
  }

  const [firstElementVisible] = useIsElementVisible(
    firstElementRef,
    observerOptions
  )

  const [lastElementVisible, hasLastElementVisibilityChanged] =
    useIsElementVisible(lastElementRef, observerOptions)

  if (lastElementVisible && hasLastElementVisibilityChanged) {
    onLastCarouselElementVisible?.()
  }

  function handleOnClickArrowLeft() {
    if (listRef.current) {
      listRef.current.scrollLeft -= 400
    }
  }

  function handleOnClickArrowRight() {
    if (listRef.current) {
      listRef.current.scrollLeft += 400
    }
  }

  return (
    <div className={cn(styles['carousel'], className)}>
      <div className={styles['carousel-header']}>
        {title && (
          <div className={styles['carousel-header-title']}>{title}</div>
        )}
        {!loading && (
          <div className={styles['carousel-header-arrows']}>
            <Button
              disabled={firstElementVisible}
              onClick={handleOnClickArrowLeft}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.BRAND}
              icon={fullArrowLeftIcon}
              iconAlt="Faire défiler le carrousel vers la gauche"
            />

            <Button
              disabled={lastElementVisible}
              onClick={handleOnClickArrowRight}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.BRAND}
              icon={fullArrowRightIcon}
              iconAlt="Faire défiler le carrousel vers la droite"
            />
          </div>
        )}
      </div>

      {loading ? (
        <div className={styles['carousel-loading']}>
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
          <AdageSkeleton isGrid />
        </div>
      ) : (
        <ul className={styles['carousel-list']} ref={listRef}>
          {elements.map((el, i) => {
            const firstRef = i === 0 ? firstElementRef : undefined
            const lastRef =
              i === elements.length - 1 ? lastElementRef : undefined
            return (
              <li key={i} ref={firstRef ?? lastRef}>
                {el}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
