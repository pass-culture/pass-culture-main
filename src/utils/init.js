import {
  // clientSignin as body,
  professionalSignin as body
} from './mock'
import { requestData } from '../reducers/request'

const init = store => {
  // mock sign
  store.dispatch(requestData(
    'POST',
    'signin',
    { body }
  ))
}

export default init
