import cn from 'classnames'
import { createRef } from 'react'

import { useIsElementVisible } from 'hooks/useIsElementVisible'
import arrowLeftIcon from 'icons/full-arrow-left.svg'
import arrowRightIcon from 'icons/full-arrow-right.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
              variant={ButtonVariant.QUATERNARYPINK}
              data-testid="carousel-arrow-left"
            >
              <SvgIcon
                src={arrowLeftIcon}
                alt="Faire défiler le carrousel vers la gauche"
                width="24"
              />
            </Button>

            <Button
              disabled={lastElementVisible}
              onClick={handleOnClickArrowRight}
              variant={ButtonVariant.QUATERNARYPINK}
              data-testid="carousel-arrow-right"
            >
              <SvgIcon
                src={arrowRightIcon}
                alt="Faire défiler le carrousel vers la droite"
                width="24"
              />
            </Button>
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
