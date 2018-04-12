import React, { Component } from 'react'
import { ROOT_PATH } from '../utils/config';

class ProfilePicture extends Component {
  render() {
    const { colored } = this.props
    return <img src={`${ROOT_PATH}/icons/ico-user-circled` + (colored ? '' : '-w') + `.svg` } alt='Avatar' {...this.props}/>
  }
}

export default ProfilePicture
