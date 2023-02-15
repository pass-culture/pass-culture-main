class PcSelectMultipleField {
  $container

  constructor({
    $container,
  }) {
    this.$container = $container
    this.bindEvents()
  }

  get $container() {
    return document.querySelector(selector)
  }

  get $select() {
    return this.$container.querySelector('select')
  }

  get $label() {
    return this.$container.querySelector('label')
  }

  bindEvents = () =>{
    this.$select.addEventListener('mousedown', (event) => {
      event.preventDefault()
      const scrollTop = this.scrollTop
      event.target.selected = !event.target.selected
      setTimeout(() => {
        this.scrollTop = scrollTop
      })
      this.focus()
    }, true)

    this.$select.addEventListener('mousemove', (event) => {
      event.preventDefault()
    })

    this.$select.addEventListener('change', this.onScrollOrChange)

    this.$select.addEventListener('scroll', this.onScrollOrChange)
  }

  onScrollOrChange = () => {
    var selected = [...this.$select.options].filter((option) => option.selected)

    if (selected.length > 0) {
      this.$label.classList.add('d-none')
      return
    }
    this.$label.classList.remove('d-none')
  }
}

class PcTomSelectMultipleFieldAutocomplete {
  autoCompleteUrl
  tomSelectSelector
  tomSelectOptions

  constructor({
    autoCompleteUrl,
    tomSelectSelector,
    tomSelectOptions,
  }) {
    this.autoCompleteUrl = autoCompleteUrl
    this.tomSelectSelector = tomSelectSelector
    this.tomSelectOptions = tomSelectOptions
    this.initializeTomSelect()
  }

  initializeTomSelect = () => {
    new TomSelect(this.tomSelectSelector, {
      plugins: ['dropdown_input', 'clear_button', 'checkbox_options'],
      persist: false,
      create: false,
      valueField: 'id',
      labelField: 'text',
      load: (query, callback) => {
        const url = `${this.autoCompleteUrl}?q=${encodeURIComponent(query)}`;
        fetch(url)
          .then((response) => response.json())
          .then((json) => callback(json.items))
          .catch((error) => callback(undefined, error));
      },
      ...this.tomSelectOptions,
    });
  }
}
