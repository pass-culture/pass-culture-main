class PcDisplaySelector extends PcAddOn {
  static CONTAINER_SELECTOR = '.pc-display-selector'
  

  get $selectors() {
    return document.querySelectorAll(PcDisplaySelector.CONTAINER_SELECTOR)
  }
  
  #getSelectorFromInput = ($input) => {
    return $input.closest(PcDisplaySelector.CONTAINER_SELECTOR)
  }
  
  #inputInSelector = ($selector) => {
    const inputName = $selector.dataset.pcInputName
    const inputSelector = 'input[name="' + inputName + '"]'
    return $selector.querySelectorAll(inputSelector)
  }

  #getSelectedValue = ($selector) => {
    let selectedValue = null
    this.#inputInSelector($selector).forEach(($input) => {
        const $target = document.getElementById($input.value)
        if($input.checked === true){
          selectedValue = $input.value
        }
      })
    return selectedValue
  }

  #change = (event) => {
    const $input = event.target
    const $selector = this.#getSelectorFromInput($input)
    this.#manageDisplay($selector)
    this.#saveConfiguration($selector)
  }

  #manageDisplay = ($selector) => {
    this.#inputInSelector($selector).forEach(($input) => {
        const $target = document.getElementById($input.value)
        if($input.checked === true){
          $target.classList.remove('d-none')
        } else {
          $target.classList.add('d-none')
        }
      })
  }

  #loadConfiguration = ($selector) => {
    if($selector.dataset.pcSaveState === "true") {
      const selectedValue = localStorage.getItem($selector.dataset.pcInputName)
      this.#inputInSelector($selector).forEach(($input) => {
        if ($input.value === selectedValue){
          $input.checked = true
        }
      })
    } else {
      localStorage.removeItem($selector.dataset.pcInputName)
    }
  }
  #saveConfiguration = ($selector) => {
    if($selector.dataset.pcSaveState === "true") {
      localStorage.setItem($selector.dataset.pcInputName, this.#getSelectedValue($selector))
    }
  }


  bindEvents = () => {
    this.$selectors.forEach(($selector) => {
      this.#loadConfiguration($selector)
      this.#inputInSelector($selector).forEach(($input) => {
          $input.addEventListener("change", this.#change)
        })
      this.#manageDisplay($selector)
      })
  }

  unbindEvents = () => {
    this.$selectors.forEach(($selector) => {
      this.#inputInSelector($selector).forEach(($input) => {
      $input.removeEventListener("change", this.#change)
        })
    })
  }
}