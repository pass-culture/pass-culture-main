import { arrayOf, bool, func, shape, string } from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

class FormFooter extends PureComponent {
  isDisplayedOnInstagram() {
    const userAgent = navigator.userAgent
    return userAgent.includes('Instagram') && userAgent.includes('iPhone')
  }

  renderFooterItem = (item, index, items) => {
    const attributes = {
      className: `${item.className || ''}`,
      disabled: item.disabled,
      id: item.id,
    }
    const renderedItem = item.url
      ? this.renderLink(item, attributes)
      : this.renderSubmitButton(item, attributes)
    const isLastItem = index + 1 === items.length

    return (
      <Fragment key={item.id}>
        {renderedItem}
        {!isLastItem && <hr />}
      </Fragment>
    )
  }

  renderSubmitButton = (item, attributes) => (
    <button
      {...attributes}
      type="submit"
    >
      {item.label}
    </button>
  )

  renderLink = (item, attributes) => (
    <Link
      {...attributes}
      onClick={item.tracker}
      onKeyPress={item.tracker}
      to={item.url}
    >
      {item.label}
    </Link>
  )

  render() {
    const { items } = this.props

    if (this.isDisplayedOnInstagram()) {
      const arbitraryValueToScrollToTheBottom = 10000
      window.scrollTo(0, arbitraryValueToScrollToTheBottom)
    }

    return (
      <footer
        className={`logout-form-footer ${
          this.isDisplayedOnInstagram() ? 'logout-form-footer-instagram' : ''
        }`}
        id="logout-form-footer"
      >
        {items.map(this.renderFooterItem)}
      </footer>
    )
  }
}

FormFooter.defaultProps = {
  items: [],
}

FormFooter.propTypes = {
  items: arrayOf(
    shape({
      className: string,
      disabled: bool,
      id: string,
      label: string.isRequired,
      tracker: func,
      url: string,
    })
  ),
}

export default FormFooter
