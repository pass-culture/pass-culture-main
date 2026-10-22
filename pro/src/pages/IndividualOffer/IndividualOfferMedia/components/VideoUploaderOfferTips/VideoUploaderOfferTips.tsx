import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Banner } from '@/design-system/Banner/Banner'
import bulbIcon from '@/icons/full-bulb.svg'

import styles from './VideoUploaderOfferTips.module.scss'
import imageVideoTips from './video-tips.svg'

export const VideoUploaderTips = () => (
  <div className={styles['video-uploader-tips']}>
    <Banner
      title="À savoir"
      icon={bulbIcon}
      description={
        <div className={styles['description']}>
          <div>
            <p className={styles['hook']}>
              "2 jeunes sur 3 aimeraient voir des vidéos sur les offres
              culturelles du pass Culture."
            </p>
            <p className={styles['text']}>Quel type de vidéo ?</p>
            <ul className={styles['list']}>
              <li>Bande annonce de votre pièce, film...</li>
              <li>Aftermovie d’une édition précédente </li>
              <li>
                Témoignages de participante, auteure, metteuse en scène...
              </li>
            </ul>
          </div>
          <SvgIcon
            className={styles['image']}
            src={imageVideoTips}
            viewBox="0 0 208 315"
            width="250"
            alt=""
            aria-hidden
          />
        </div>
      }
    />
  </div>
)
