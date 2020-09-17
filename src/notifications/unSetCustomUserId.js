import { getBatchSDK } from './setUpBatchSDK'

export default () => {
  const config = {
    batchIsEnabled: process.env.BATCH_IS_ENABLED,
  }
  if (config.batchIsEnabled === 'true') {
    getBatchSDK()

    /* eslint-disable-next-line */
    window.batchSDK(function(api) {
      api.ui.hide('alert')
      api.setCustomUserID(null)
    })
  }
}
