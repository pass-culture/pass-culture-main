import { createRef, useEffect } from 'react'

import { doesUserPreferReducedMotion } from 'utils/windowMatchMedia'

import styles from './AdageDiscoveryBanner.module.scss'

export function AdageDiscoveryBanner() {
  const circlesGroupRef = createRef<SVGGElement>()
  const crossesGroupRef = createRef<SVGGElement>()
  const ovalsGroupRef = createRef<SVGGElement>()

  useEffect(() => {
    if (doesUserPreferReducedMotion()) {
      return
    }

    function translateYWithSpeed(speed: number) {
      return `translateY(${-window.scrollY / speed}px)`
    }

    const onDocumentScroll = () => {
      if (circlesGroupRef.current) {
        circlesGroupRef.current.style.transform = translateYWithSpeed(4)
      }

      if (ovalsGroupRef.current) {
        ovalsGroupRef.current.style.transform = translateYWithSpeed(8)
      }

      if (crossesGroupRef.current) {
        crossesGroupRef.current.style.transform = translateYWithSpeed(10)
      }
    }
    document.addEventListener('scroll', onDocumentScroll)

    return () => document.removeEventListener('scroll', onDocumentScroll)
  }, [circlesGroupRef, crossesGroupRef, ovalsGroupRef])

  return (
    <div className={styles['discovery-banner']}>
      <h1 className={styles['discovery-banner-title']}>
        Découvrez{' '}
        <span className={styles['discovery-banner-title-highlight']}>
          la part collective
        </span>{' '}
        du pass Culture
      </h1>
      <div className={styles['discovery-banner-background']}>
        <svg height="100%" width="100%" xmlns="http://www.w3.org/2000/svg">
          <g ref={ovalsGroupRef} data-testid="banner-ovals-group">
            <path
              className={styles['discovery-banner-svg-oval']}
              d="M 770.3748 120.3299 L 875.9414 102.4711 C 912.2112 96.8435 920.2713 142.5543 885.61 148.666 L 779.428 167.3888 C 743.3013 173.7589 733.5036 126.8313 770.3521 120.2218 Z M 957.4883 87.3367 L 1063.0549 69.478 C 1099.3247 63.8503 1107.3848 109.5611 1072.7235 115.6729 L 966.5415 134.3956 C 930.4148 140.7657 920.6171 93.8381 957.4655 87.2287 Z"
            />
          </g>
          <g ref={circlesGroupRef}>
            <circle
              id="banner-circle"
              cx="20px"
              cy="40%"
              r="6"
              className={styles['discovery-banner-svg-circle']}
            />
            <use href="#banner-circle" x="85%" y="-20%" />
            <use href="#banner-circle" x="95%" y="45%" />
            <use href="#banner-circle" x="140%" y="-10%" />
          </g>
          <g ref={crossesGroupRef}>
            <path
              id="banner-cross"
              d="M50.5457 38.999C49.2838 39.1453 48.1353 38.2882 47.8915 37.0579L47.861 36.8607L47.2485 31.5772L41.968 32.1894C40.635 32.3439 39.4294 31.3907 39.2752 30.0611C39.129 28.7996 39.9836 27.6505 41.2129 27.4068L41.4098 27.3748L46.6905 26.7641L45.9662 20.5171C45.8114 19.1814 46.762 17.9752 48.0889 17.8213C49.3524 17.6749 50.4994 18.5321 50.743 19.7609L50.775 19.958L51.4994 26.2065L57.7411 25.4829C59.0741 25.3284 60.2795 26.2801 60.4335 27.6081C60.5799 28.8711 59.7253 30.0203 58.4961 30.264L58.299 30.2945L52.0574 31.0196L52.67 36.3031C52.8247 37.6372 51.8727 38.8452 50.5457 38.999Z"
              className={styles['discovery-banner-svg-cross']}
            />
            <use href="#banner-cross" x="50%" transform="rotate(5)" />
            <use href="#banner-cross" x="70%" y="10%" />
            <use href="#banner-cross" x="25%" y="70%" />
          </g>
        </svg>
      </div>
    </div>
  )
}
