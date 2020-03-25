import React, { PureComponent } from 'react'
import lottie from 'lottie-web'
import animation from './animation.json'

class LoadingAnimation extends PureComponent {
  componentDidMount() {
    lottie.loadAnimation({
      container: document.getElementById('loading-animation'),
      renderer: 'svg',
      loop: true,
      autoplay: true,
      animationData: animation,
    })
  }

  render() {
    return <div id="loading-animation" />
  }
}

export default LoadingAnimation
