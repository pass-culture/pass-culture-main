import {
  AnimatePresence,
  easeOut,
  motion,
  useReducedMotion,
} from 'framer-motion'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useCurrentUser } from '@/commons/hooks/useCurrentUser'
import { WEBAPP_URL } from '@/commons/utils/config'
import fullLinkIcon from '@/icons/full-link.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './HeadlineOffer.module.scss'

export function HeadlineOffer(): JSX.Element | null {
  const { logEvent } = useAnalytics()
  const { currentUser } = useCurrentUser()
  const { isHeadlineOfferAllowedForOfferer, headlineOffer } =
    useHeadlineOfferContext()

  const show = Boolean(isHeadlineOfferAllowedForOfferer && headlineOffer)
  // const prefersReduced = useReducedMotion()

  // const transition = prefersReduced
  //   ? { duration: 0 }
  //   : { duration: 0.35, ease: easeOut }

  if (!show) {
    return null
  }

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${headlineOffer?.venueId}`

  return (
    <AnimatePresence mode="wait">
      {show && (
        // <motion.div
        //   layout
        //   initial={{ x: -40, opacity: 0, height: 0 }}
        //   animate={{ x: 0, opacity: 1, height: 'auto' }}
        //   exit={{ x: -40, opacity: 0, height: 0 }}
        //   transition={transition}
        //   style={{ overflow: 'hidden' }}
        // >
        <motion.div
          key={`${headlineOffer!.id}`}
          layout
          initial={{ x: -90, opacity: 0, height: 0 }}
          animate={{ x: 0, opacity: 1, height: 'auto' }}
          exit={{ x: -60, opacity: 0, height: 0 }}
          transition={{
            type: 'spring',
            stiffness: 380,
            damping: 32,
            mass: 0.9,
          }}
          style={{ overflow: 'hidden' }}
        >
          <motion.div
            initial={{ scaleX: 0.98, scaleY: 1.02 }}
            animate={{ scaleX: 1, scaleY: 1 }}
            transition={{ type: 'spring', stiffness: 500, damping: 38 }}
          >
            <div className={styles['headline-offer-container']}>
              <div className={styles['headline-offer-title-container']}>
                <h2 className={styles['headline-offer-title']}>
                  Votre offre à la une
                </h2>
                <ButtonLink
                  variant={ButtonVariant.QUATERNARY}
                  icon={fullLinkIcon}
                  to={venuePreviewLink}
                  isExternal
                  opensInNewTab
                  onClick={() => {
                    logEvent(Events.CLICKED_VIEW_APP_HEADLINE_OFFER, {
                      offerId: headlineOffer?.id,
                      userId: currentUser.id,
                    })
                  }}
                >
                  Visualiser dans l’application
                </ButtonLink>
              </div>

              <div className={styles['headline-offer-block']}>
                <Thumb
                  className={styles['headline-offer-thumb']}
                  url={headlineOffer?.image?.url}
                />
                <p className={styles['headline-offer-name']}>
                  {headlineOffer?.name}
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
