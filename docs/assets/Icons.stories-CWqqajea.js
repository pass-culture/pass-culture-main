import{j as t}from"./jsx-runtime-u17CrQMm.js";import{r as m}from"./iframe-BxvkzIaT.js";import{S as d}from"./SvgIcon-DuZPzNRk.js";import{s as u}from"./stroke-search-Bph5aoaJ.js";import{f as h,s as v,o as _}from"./iconsList-DTbNHR9H.js";import{T as y}from"./TextInput-Bnhe8IQn.js";import"./preload-helper-PPVm8Dsz.js";import"./full-thumb-up-Bb4kpRpM.js";import"./full-bulb-PM9lEXbZ.js";import"./full-clear-Q4kCtSRL.js";import"./full-close-5Oxr7nnd.js";import"./full-down-Cmbtr9nI.js";import"./full-download-XQM5pv74.js";import"./full-duplicate-BZV8LNX-.js";import"./full-edit-CxAaM2Fv.js";import"./full-error-BFAmjN4t.js";import"./full-show-BUp4jmvL.js";import"./full-info-D24AtBVt.js";import"./full-left-vjwAEs82.js";import"./full-link-CYVo23DH.js";import"./full-location-CVEaH-Cp.js";import"./full-more-Cfm5WMtk.js";import"./full-next-B_76kGmE.js";import"./full-refresh-BZh6W0mB.js";import"./full-right-Dd3YsyCq.js";import"./full-three-dots-6wSZh7oi.js";import"./full-up-D6TPt2ju.js";import"./full-validate-CbMNulkZ.js";import"./stroke-close-DnlFsd1c.js";import"./stroke-date-CWTXq8J4.js";import"./stroke-price-CbFScctA.js";import"./stroke-error-DSZD431a.js";import"./stroke-pass-CALgybTM.js";import"./stroke-picture-VF2OicDu.js";import"./stroke-thing-O6UIROL8.js";import"./stroke-trash-Cc_5v2lW.js";import"./stroke-user-u-f9pznf.js";import"./stroke-video-Cd5kQZzx.js";import"./stroke-wrong-BAouvvNg.js";import"./index-DjmZOsWy.js";import"./FieldFooter-CAPLYfea.js";import"./index.module-Dejjbhs_.js";import"./FieldHeader-BRuaF6KE.js";import"./Tooltip-DXXoOPLJ.js";const I="_title_1490c_1",x="_container_1490c_28",N="_name_1490c_41",f="_icon_1490c_7",e={title:I,"icon-stories":"_icon-stories_1490c_7","icon-list":"_icon-list_1490c_13","search-input-container":"_search-input-container_1490c_21",container:x,name:N,"name-container":"_name-container_1490c_44","copy-to-clipboard":"_copy-to-clipboard_1490c_48","icon-container":"_icon-container_1490c_51","copy-to-clipboard-wrapper":"_copy-to-clipboard-wrapper_1490c_59",icon:f},g=(i,a)=>(i=".*"+i.toLowerCase().split("").join(".*")+".*",new RegExp(i).test(a.toLowerCase())),w=[{title:"Full icons",icons:h},{title:"Stroke icons",icons:v},{title:"Other icons",icons:_}],r=()=>{const[i,a]=m.useState(""),n=async o=>{o.persist();const c=o.currentTarget;await navigator.clipboard.writeText(c.getAttribute("data-src")??""),c.classList.add(e["copy-to-clipboard"]);const s=setTimeout(()=>{c.classList.remove(e["copy-to-clipboard"]),clearTimeout(s)},600)};return t.jsxs("div",{className:e["icon-stories"],children:[t.jsx("div",{className:e["search-input-container"],children:t.jsx(y,{name:"search",label:"Rechercher une icon",icon:u,onChange:o=>a(o.target.value),value:i})}),w.map(o=>{const c=o.icons.filter(s=>g(i,s.src));return c.length===0?null:t.jsxs("div",{children:[t.jsx("h1",{className:e.title,children:o.title}),t.jsx("div",{className:e["icon-list"],children:c.map(s=>{const l=s.src.split("/"),p=l[l.length-1].split(".")[0].replace("full-","").replace("stroke-","").replace("shadow-","");return t.jsxs("div",{className:e.container,onClick:n,"data-src":s.src,children:[t.jsx("div",{className:e["copy-to-clipboard-wrapper"],children:t.jsx("span",{children:"Copié !"})}),t.jsx("div",{className:e["icon-container"],children:t.jsx(d,{src:s.src,alt:s.src,viewBox:s.viewBox,className:e.icon})}),t.jsx("div",{className:e["name-container"],children:t.jsx("span",{className:e.name,children:p})})]},s.src)})})]},o.title)})]})},ht={title:"@/icons/Icons"};r.parameters={...r.parameters,docs:{...r.parameters?.docs,source:{originalSource:`() => {
  const [searchInput, setSearchInput] = useState('');
  const onClick = async (e: React.MouseEvent<HTMLDivElement>) => {
    e.persist();
    const target = e.currentTarget as Element;
    await navigator.clipboard.writeText(target.getAttribute('data-src') ?? '');
    target.classList.add(styles['copy-to-clipboard']);
    const timeoutId = setTimeout(() => {
      target.classList.remove(styles['copy-to-clipboard']);
      clearTimeout(timeoutId);
    }, 600);
  };
  return <div className={styles['icon-stories']}>
      <div className={styles['search-input-container']}>
        <TextInput name="search" label='Rechercher une icon' icon={strokeSearchIcon} onChange={event => setSearchInput(event.target.value)} value={searchInput} />
      </div>

      {iconsSections.map(section => {
      const filteredIcons = section.icons.filter(iconListItem => fuzzyMatch(searchInput, iconListItem.src));
      if (filteredIcons.length === 0) {
        return null;
      }
      return <div key={section.title}>
            <h1 className={styles['title']}>{section.title}</h1>

            <div className={styles['icon-list']}>
              {filteredIcons.map(icon => {
            const fileNameParts = icon.src.split('/');
            const iconName = fileNameParts[fileNameParts.length - 1].split('.')[0].replace('full-', '').replace('stroke-', '').replace('shadow-', '');
            return <div key={icon.src} className={styles['container']} onClick={onClick} data-src={icon.src}>
                    <div className={styles['copy-to-clipboard-wrapper']}>
                      <span>
                        Copié !
                      </span>
                    </div>

                    <div className={styles['icon-container']}>
                      <SvgIcon src={icon.src} alt={icon.src} viewBox={icon.viewBox} className={styles['icon']} />
                    </div>

                    <div className={styles['name-container']}>
                      <span className={styles['name']}>{iconName}</span>
                    </div>
                  </div>;
          })}
            </div>
          </div>;
    })}
    </div>;
}`,...r.parameters?.docs?.source}}};const vt=["Icons"];export{r as Icons,vt as __namedExportsOrder,ht as default};
