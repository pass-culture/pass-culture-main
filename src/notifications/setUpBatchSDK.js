const config = {
  batchIsEnabled: process.env.BATCH_IS_ENABLED,
}

export default function setupBatchSDK() {
  if (config.batchIsEnabled === 'true') {
    getBatchSDK()
    const batchSDKUIConfig = {
      alert: {
        attach: 'top center',
        autoShow: false,
        btnWidth: '200',
        positiveSubBtnLabel: 'Activer les notifications',
        negativeBtnLabel: 'Plus tard',
        positiveBtnStyle: { backgroundColor: '#eb0055', hoverBackgroundColor: '#c10046' },
        icon: 'favicon.ico',
        text:
          'Découvre les nouvelles offres en exclusivité sur ton pass en activant les notifications !',
      },
    }

    /* Finalize the Batch SDK setup */
    /* eslint-disable-next-line */
    window.batchSDK('setup', {
      apiKey: process.env.BATCH_API_KEY,
      subdomain: process.env.BATCH_SUBDOMAIN,
      authKey: process.env.BATCH_AUTH_KEY,
      vapidPublicKey: process.env.BATCH_VAPID_PUBLIC_KEY,
      ui: batchSDKUIConfig,
      defaultIcon: 'favicon.ico', // for Chrome desktop
      smallIcon: 'favicon.ico', // for Chrome Android
      sameOrigin: process.env.BATCH_SAME_ORIGIN === 'true',
      useExistingWorker: true,
    })

    /* eslint-disable-next-line */
    window.batchSDK(api => {
      api.ui.show('alert')
    })
  }
}

export const setCustomUserId = userId => {
  if (config.batchIsEnabled === 'true') {
    getBatchSDK()
    /* eslint-disable-next-line */
    window.batchSDK(function (api) {
      api.setCustomUserID(userId)
    })
  }
}

export const getBatchSDK = () => {
  /* Load remote Batch SDK JavaScript code */
  /* eslint-disable-next-line */
  ;(function (b, a, t, c, h, e, r) {
    h = 'batchSDK'
    b[h] =
      b[h] ||
      function () {
        /* eslint-disable-next-line */
        ;(b[h].q = b[h].q || []).push(arguments)
      }
    ;(e = a.createElement(t)), (r = a.getElementsByTagName(t)[0])
    /* eslint-disable-next-line */
    e.async = 1
    e.src = c
    r.parentNode.insertBefore(e, r)
  })(window, document, 'script', 'https://via.batch.com/v2/bootstrap.min.js')
}
