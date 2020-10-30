import setupBatchSDK from '../../notifications/setUpBatchSDK'

const Traking = () => {
  if (window.location.href === 'https://app.passculture.beta.gouv.fr/beta') {
    window.snaptr('track', 'PAGE_VIEW')
    window.fbq('track', 'PageView')
  }

  setupBatchSDK()

  return null
}

export default Traking
