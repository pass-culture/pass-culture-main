class PcBackofficeApp {
  tooltips

  constructor() {
    this.bindEvents()
    this.initializePcSelects()
    this.initializeTooltips()
  }

  get $pcSelects() {
    return document.querySelectorAll('.pc-select')
  }

  get $forms() {
    return document.forms
  }

  get $tooltips() {
    return document.querySelectorAll('[data-toggle="tooltip"]')
  }

  bindEvents = () => {
    [...this.$forms].forEach(($form) => {
      $form.addEventListener("submit", this.onFormSubmit, false);
    })
  }

  onFormSubmit = (event) => {
    event.preventDefault();
    const form = event.target;
    if (form.checkValidity()) {
      form.submit();
    }
  }

  initializeTooltips = () => {
    this.$tooltips.forEach(($tooltip) => {
      this.tooltips.push(new bootstrap.Tooltip($tooltip))
    })
  }

  initializePcSelects = () => {
    this.$pcSelects.forEach(($pcSelect) => {
      const settings = {
        plugins: ['dropdown_input', 'clear_button', 'checkbox_options'],
        persist: false,
        create: false,

      };
      new TomSelect($pcSelect, settings);
    })
  }
}
