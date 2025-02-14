/**
Manage tables to make them dynamic
 */
class PcTableManager extends PcAddOn {
  static SELECTOR = '.pc-table-manager'
  static DRAGGABLE =  '.pc-table-manager-draggable'
  static VISIBILITY = '.pc-table-manager-toggle-visibility'

  get $tables() {
    return document.querySelectorAll(PcTableManager.SELECTOR)
  }

  #getConfigurationUniqueId = (configurationId) => {
    const baseUrl = window.location.href.toString().split(window.location.host)[1].split('?')[0]
    let configurationUniqueId = 'PcTableManager@' + configurationId + "@"
    baseUrl.split('/').forEach((element) => {
      if (element === ''){}
      else if (!isNaN(element)){
        configurationUniqueId += '/ID'
      } else {
        configurationUniqueId += ('/' + element)
      }
    })
    return configurationUniqueId
  }

  #mergeConfigurations = (configuration, defaultConfiguration) => {
    if (configuration === null){
      return defaultConfiguration
    }
    // create mappings to move from two quadratic expressions to four linear ones
    const columns = configuration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});

    const defaultColumns = defaultConfiguration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});
    // add missing columns with default values
    defaultConfiguration.columns.forEach((column) => {
      if(columns[column.id] === undefined) {
        configuration.columns.push(column)
      }
    })
    // remove deleted columns
    const toDelete = []
    if (configuration.columns.length !== defaultConfiguration.columns.length) {
      configuration.columns.forEach((column) => {
      if(defaultColumns[column.id] === undefined) {
        toDelete.push(column)
      }
    })
    toDelete.forEach((column) => {
      configuration.columns.splice(configuration.columns.indexOf(column), 1)
    })
    }
    return configuration
  }


  #initializeTableFromHtml = ($table) => {
    const lines = $table.querySelectorAll("tr")
    const configuration = this.#initializeHeaders($table)
    lines.forEach(($line) => {
      const cells = $line.querySelectorAll("td")
      if (cells !== null){
        for(let i=0; i < Math.min(cells.length, configuration.columns.length); i++){
          cells[i].classList.add(configuration.columns[i].id)
        }
      }
    })
    return configuration
  }

  #initializeHeaders = ($table) => {
    let headerNumber = 0
    const configuration = {
      id: $table.dataset.pcTableManagerId,
      columns: []
    }
    $table.querySelectorAll("th").forEach(($column) => {
      headerNumber++
      const columnConfiguration = {}
      const text_content = $column.textContent.replaceAll(/\n/g, '').trim()
      columnConfiguration.id = text_content.replaceAll(/[^a-zA-Z0-9]/g, '')
      if (columnConfiguration.id === ''){
        columnConfiguration.id = ($column.dataset.pcColumnName || ("default-headerNumber")).replaceAll(/[^a-zA-Z0-9]/g, '')
      }
      columnConfiguration.id = "column-" + columnConfiguration.id 
      columnConfiguration.name = $column.dataset.pcColumnName || text_content
      columnConfiguration.display = ($column.dataset.pcDisplayColumn || "true") == "true"
      configuration.columns.push(columnConfiguration)

      $column.classList.add(columnConfiguration.id)
    })
    return configuration
  }
  /** MENU **/
  #initializeMenu = ($table, configuration) => {
    const div = document.createElement('div')
    div.classList.add('dropdown')
    const elements = []
    configuration.columns.forEach((column) => {
      elements.push(
        `
          <li class="dropdown-item me-3" draggable="true" data-pc-target-column-id="${column.id}">
            <i class="bi bi-grip-vertical"></i>
            ${column.name}
            <i class="bi pc-table-manager-toggle-visibility link-primary h5 position-absolute end-0 pe-2 bi-eye${column.display?'':'-slash'}"></i>
          </li>
        `
      )
    })

    const innerHTML = `
      <button class="btn p0" type="button" data-bs-toggle="dropdown" aria-expanded="false">
        <i class="bi bi-three-dots-vertical"></i>
      </button>
      <ul class="dropdown-menu pc-table-manager-draggable" data-pc-target-table-id="${configuration.id}">
        ${elements.join("\n")}
      </ul>
    `
    div.innerHTML = innerHTML
    $table.before(div)
  }

  #onVisibilityToggleClick = (event) => {
    event.stopPropagation()
    const configuration = this.#getConfigurationForEdit(event.target.parentElement.parentElement.dataset.pcTargetTableId)
    const columnId = event.target.parentElement.dataset.pcTargetColumnId
    configuration.columns.forEach((column) => {
      if (column.id == columnId){
        column.display = !event.target.classList.contains('bi-eye')
      }
    })

    if (event.target.classList.contains('bi-eye')){
      event.target.classList.remove('bi-eye')
      event.target.classList.add('bi-eye-slash')
    } else {
      event.target.classList.add('bi-eye')
      event.target.classList.remove('bi-eye-slash')
    }
    this.applyConfiguration(configuration)
  }

  /** DRAG AND DROP **/
  #isValidTarget = ($element) => {
    return $element.tagName === 'LI' && $element.classList.contains('dropdown-item')
  }

  #onDragStart = (event) => {
    // on a setTimeout to do it once the dragstart event is finished
    event.target.parentElement.dataset.pcTableManagerDraggableHeight = event.target.getBoundingClientRect().height
    setTimeout(() => {
      event.target.classList.add('d-none')
      event.target.parentElement.appendChild(event.target) // small hack to avoir graophical glicth
    }, 0)
  }

  #onDragEnd = (event) => {
    // on a setTimeout to do it once the dragend event is finished
    const $parent = event.target.parentElement
    setTimeout(() => {event.target.classList.remove('d-none')}, 0)
    delete event.target.parentElement.dataset.pcTableManagerDraggableHeight
    const $dropTarget = $parent.querySelector('.pc-table-manager-target')
    if($dropTarget !== null) {
      if ($dropTarget.dataset.position === 'after') {
        $dropTarget.before(event.target)
      } else {
        $dropTarget.after(event.target)
      }
      $dropTarget.classList.remove('pc-table-manager-target')
      $dropTarget.style.paddingTop = ''
      $dropTarget.style.paddingBottom = ''
    }
    //compute and render new table
    const configuration = this.#getConfigurationForEdit($parent.dataset.pcTargetTableId)
    const columnsMap = configuration.columns.reduce((map, obj) => {
      map[obj.id] = obj;
      return map;
    }, {});
    const newColumns = []
    for(let i = 0; i < $parent.children.length; i++){
      newColumns.push(columnsMap[$parent.children[i].dataset.pcTargetColumnId])
    }
    configuration.columns = newColumns
    this.applyConfiguration(configuration)
  }

  #onDragOver = (event) => {
    const $target = event.target
    if(this.#isValidTarget($target)) {  
      const targetBox = $target.getBoundingClientRect()
      const position = (event.clientY - targetBox.top) / targetBox.height
      $target.classList.add('pc-table-manager-target')
      if (position < 0.5) {
        // we are on the top part of the target
        if($target.style.paddingTop == '') {
          //manage a clean spacing when moving the element
          const rawPadding = window.getComputedStyle($target, null).getPropertyValue('padding-top')
          let padding = parseInt(rawPadding.replace(/[^0-9]/g, ''))
          padding += parseInt($target.parentElement.dataset.pcTableManagerDraggableHeight)
          $target.style.paddingTop = padding + 'px'
          $target.style.paddingBottom = ''

        }
        $target.dataset.position = 'after'
      } else {
        // we are on the bottom part of the target
        if($target.style.paddingBottom == '') {
          //manage a clean spacing when moving the element
          const rawPadding = window.getComputedStyle($target, null).getPropertyValue('padding-bottom')
          let padding = parseInt(rawPadding.replace(/[^0-9]/g, ''))
          padding += parseInt($target.parentElement.dataset.pcTableManagerDraggableHeight)
          $target.style.paddingBottom = padding + 'px'
          $target.style.paddingTop = ''
        }
        $target.dataset.position = 'before'
      }
      if ($target.previousElementSibling !== null) {
        $target.previousElementSibling.classList.remove('pc-table-manager-target')
        $target.previousElementSibling.style.paddingBottom = ''
        $target.previousElementSibling.style.paddingTop = ''
        delete $target.previousElementSibling.dataset.position
      }
      if ($target.nextElementSibling !== null) {
        $target.nextElementSibling.classList.remove('pc-table-manager-target')
        $target.nextElementSibling.style.paddingBottom = ''
        $target.nextElementSibling.style.paddingTop = ''
        delete $target.nextElementSibling.dataset.position
      }
    }
  }
  /** END DRAG AND DROP **/

  #getConfigurationForEdit = (id) => {
    return structuredClone(this.configurations[id])
  }

  #needUpdate = (previousConfiguration, configuration) => {
    for(let i=0; i<previousConfiguration.columns.length; i++){
      if (
        previousConfiguration.columns[i].id != configuration.columns[i].id
        || previousConfiguration.columns[i].display != configuration.columns[i].display
      ){
        return true
      }
    }
    return false
  }

  initialize = () => {
    this.configurations = {}
    this.$tables.forEach(($table) => {
      const defaultConfiguration = this.#initializeTableFromHtml($table)
      this.configurations[defaultConfiguration.id] = defaultConfiguration
      const oldConfiguration = this.getConfiguration(defaultConfiguration.id)
      const configuration = this.#mergeConfigurations(oldConfiguration, defaultConfiguration)
      this.applyConfiguration(configuration)
      this.#initializeMenu($table, configuration)
    })
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'dragstart', PcTableManager.DRAGGABLE, this.#onDragStart)
    EventHandler.on(document.body, 'dragend', PcTableManager.DRAGGABLE, this.#onDragEnd)
    EventHandler.on(document.body, 'dragover', PcTableManager.DRAGGABLE, this.#onDragOver)
    EventHandler.on(document.body, 'click', PcTableManager.VISIBILITY, this.#onVisibilityToggleClick)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'dragstart', PcTableManager.DRAGGABLE, this.#onDragStart)
    EventHandler.off(document.body, 'dragend', PcTableManager.DRAGGABLE, this.#onDragEnd)
    EventHandler.off(document.body, 'dragover', PcTableManager.DRAGGABLE, this.#onDragOver)
    EventHandler.off(document.body, 'click', PcTableManager.VISIBILITY, this.#onVisibilityToggleClick)
  }

  applyConfiguration = (configuration) => {
    // Only in prototype
    const startTime = performance.now()

    const previousConfiguration = this.configurations[configuration.id]
    const $table = document.querySelector(`table[data-pc-table-manager-id="${configuration.id}"]`);
    
    if(! this.#needUpdate(previousConfiguration, configuration)){
      // fast path to not blink the table if nothing changed
      $table.classList.remove('d-none')
      this.saveConfiguration(configuration)
      this.configurations[configuration.id] = configuration
      return
    }

    $table.classList.add('d-none')
    const oldConfigurationMap = {}

    $table.querySelectorAll("tr").forEach(($line) => {
      configuration.columns.forEach((columnConfiguration) => {
        // retrieve cell to move/update
        let $cell
        if (oldConfigurationMap[columnConfiguration.id] === undefined) {
          for(let i=0; i < $line.children.length; i++){
            if ($line.children[i].classList.contains(columnConfiguration.id)){
              $cell = $line.children[i]
              oldConfigurationMap[columnConfiguration.id] = i
              break
            }
          }
        } else {
          $cell = $line.children[oldConfigurationMap[columnConfiguration.id]]
        }

        // apply configuration
        if(columnConfiguration.display){
          $cell.classList.remove('d-none')
          $line.appendChild($cell)
        } else {
          $cell.classList.add('d-none')
        }
      })
    })
    $table.classList.remove('d-none')
    this.saveConfiguration(configuration)
    this.configurations[configuration.id] = configuration

    // Only in prototype

    const endTime = performance.now()
    console.log(`configuration applied in  ${endTime - startTime} milliseconds`)
  }

  saveConfiguration = (configuration) => {
    localStorage.setItem(this.#getConfigurationUniqueId(configuration.id), JSON.stringify(configuration))
  }

  getConfiguration = (configurationId) => {
    const rawConfiguration = localStorage.getItem(this.#getConfigurationUniqueId(configurationId))
    if(rawConfiguration){
      return JSON.parse(rawConfiguration)
    }
    return null
  }


}
