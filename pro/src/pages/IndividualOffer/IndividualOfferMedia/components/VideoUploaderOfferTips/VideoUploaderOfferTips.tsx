import { TipsBanner } from 'ui-kit/TipsBanner/TipsBanner'

import imageVideoTips from './video-tips.png'
import styles from './VideoUploaderOfferTips.module.scss'

export const VideoUploaderTips = () => (
  <TipsBanner decorativeImage={imageVideoTips}>
    <>
      <p className={styles['hook']}>
        "2 jeunes sur 3 aimeraient voir des vidéos sur les offres culturelles du
        pass Culture."
      </p>
      <p className={styles['text']}>Quel type de vidéo ?</p>
      <ul className={styles['list']}>
        <li>Bande annonce de votre pièce, film...</li>
        <li>Aftermovie d’une édition précédente </li>
        <li>Témoignages de participante, auteure, metteuse en scène...</li>
      </ul>
    </>
  </TipsBanner>
)
