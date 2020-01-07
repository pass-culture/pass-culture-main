import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Transition } from 'react-transition-group'

import { closeSharePopin } from '../../../reducers/share'
import Icon from '../Icon/Icon'

const transitionDelay = 500
const transitionDuration = 250

const defaultStyle = {
  transitionDuration: `${transitionDuration}ms`,
  transitionProperty: 'bottom',
  transitionTimingFunction: 'ease',
}

const transitionStyles = {
  entered: { bottom: 0, opacity: 1 },
  entering: { bottom: '-100%', opacity: 1 },
  exited: { bottom: '-100%', opacity: 0 },
  exiting: { bottom: '-100%', opacity: 0 },
}

class SharePopin extends PureComponent {
  handleCloseHandler = () => {
    const { dispatch, options } = this.props
    const { handleClose } = options
    if (handleClose) {
      handleClose()
    }
    dispatch(closeSharePopin())
  }

  renderCloseButton = () => (
    <button
      className="pc-text-button is-absolute fs16"
      id="share-popin-close-button"
      onClick={this.handleCloseHandler}
      type="button"
    >
      <Icon
        alt="Fermer la popin de partage"
        svg="ico-close"
      />
    </button>
  )

  render() {
    const { visible, options } = this.props
    const { buttons, text, title } = options || {}

    return (
      <Transition
        in={visible}
        timeout={transitionDelay}
      >
        {status => (
          <div
            className={`is-absolute mx6 mt6 transition-${status}`}
            id="share-popin"
            style={{ ...defaultStyle, ...transitionStyles[status] }}
          >
            {options && (
              <div className="pc-theme-gradient inner is-relative is-clipped">
                {this.renderCloseButton()}
                <div
                  className="fs16 text-left"
                  id="share-popin-fixed-container"
                >
                  <div className="ml24 mr48 mt20 mb32">
                    <h3>
                      <span className="is-bold">
                        {title}
                      </span>
                    </h3>
                    <p className="mt18">
                      <span>
                        {text}
                      </span>
                    </p>
                  </div>
                  <div className="dotted-top-white flex-columns flex-around">
                    {buttons}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </Transition>
    )
  }
}

SharePopin.defaultProps = {
  options: {
    buttons: [],
    handleClose: null,
    text: null,
    title: null,
  },
}

SharePopin.propTypes = {
  dispatch: PropTypes.func.isRequired,
  options: PropTypes.shape({
    buttons: PropTypes.arrayOf(PropTypes.object),
    handleClose: PropTypes.func,
    text: PropTypes.string,
    title: PropTypes.string,
  }),
  visible: PropTypes.bool.isRequired,
}

export default SharePopin
