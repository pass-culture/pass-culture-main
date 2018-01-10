
import { clientSignin, professionalSignin } from './mock'
import { requestData } from '../reducers/request'

const init = store => {
  // mock sign
  store.dispatch(requestData(
    'POST',
    'signin',
    {
      // body: clientSignin,
      body: professionalSignin
    }
  ))
}

export default init
