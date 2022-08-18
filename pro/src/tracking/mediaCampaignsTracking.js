const LARGE_MULTIPLER = 10000000000000

const TYPE = 'site'

/* Beware : the same function is defined for id-check */
// TODO(antoinewg): do we still use Floodlight tracking ?
const createTrackingIframe = cat => {
  const randomInteger = Math.random() * LARGE_MULTIPLER

  const iframeId = `floodlight-cat-${cat}`
  const existingIframe = document.getElementById(iframeId)
  if (existingIframe) {
    return
  }

  const iframe = document.createElement('iframe')
  iframe.id = iframeId
  iframe.src =
    `https://10483184.fls.doubleclick.net/activityi;src=10483184;type=${TYPE};cat=${cat};dc_lat=;dc_rdid=;tag_for_child_directed_treatment=;tfua=;npa=;` +
    'gdpr=${GDPR};gdpr_consent=${GDPR_CONSENT_755};' +
    `ord=1;num=${randomInteger}?`
  iframe.width = '1'
  iframe.height = '1'
  iframe.frameborder = '0'
  iframe.style = 'display:none'

  document.body.appendChild(iframe)
}

export const campaignTracker = {
  signUp: () => createTrackingIframe('passc0'),
  signUpValidation: () => createTrackingIframe('passc00'),
}
