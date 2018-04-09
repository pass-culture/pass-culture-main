import { setGeolocationPosition } from '../reducers/geolocation'

import { IS_DEV } from '../utils/config'

const init = store => {
  var watchID = navigator.geolocation.watchPosition(function(position) {
    store.dispatch(setGeolocationPosition(position))
  });
}

export default init
