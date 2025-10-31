import{j as v}from"./jsx-runtime-CUHZkl-4.js";import{c as wt}from"./index-Mtezvp0m.js";import{s as Tt}from"./full-more-DLJb58kc.js";import{S as At}from"./SvgIcon-rwPqqgqt.js";import{r as N}from"./iframe-Bvsmtro0.js";import"./config-BqmKEuqZ.js";import{u as Dt}from"./chunk-OIYGIGL5-DM2wn0Bs.js";import"./reducer-CgRhu10x.js";import"./testUtils-COv8CuEG.js";const pe={"image-placeholder":"_image-placeholder_3ixx5_1","image-placeholder-text":"_image-placeholder-text_3ixx5_12"};function Ce({className:t}){return v.jsxs("div",{className:wt(pe["image-placeholder"],t),children:[v.jsx(At,{alt:"",src:Tt,width:"48"}),v.jsx("p",{className:pe["image-placeholder-text"],children:"Image corrompue, veuillez ajouter une nouvelle image"})]})}try{Ce.displayName="ImagePlaceholder",Ce.__docgenInfo={description:"",displayName:"ImagePlaceholder",props:{className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}}}}}catch{}const Rt=t=>{const e=N.useRef();return N.useEffect(()=>{e.current=t}),e.current};function _e({src:t,alt:e,className:a,testId:n,placeholder:s}){const[r,i]=N.useState(!1),o=Rt(t);return N.useEffect(()=>{t!==o&&i(!1)},[t,o]),r?s:v.jsx("img",{className:a,src:t,alt:e,onError:()=>i(!0),"data-testid":n})}try{_e.displayName="SafeImage",_e.__docgenInfo={description:"",displayName:"SafeImage",props:{src:{defaultValue:null,description:"",name:"src",required:!0,type:{name:"string"}},alt:{defaultValue:null,description:"",name:"alt",required:!0,type:{name:"string"}},placeholder:{defaultValue:null,description:"",name:"placeholder",required:!0,type:{name:"ReactNode"}},className:{defaultValue:null,description:"",name:"className",required:!1,type:{name:"string"}},testId:{defaultValue:null,description:"",name:"testId",required:!1,type:{name:"string"}}}}}catch{}const Ot=t=>typeof t=="object"&&t!==null&&"message"in t,Lt=t=>Ot(t)&&"name"in t&&t.name==="ApiError",Js=(t,e="Une erreur s’est produite, veuillez réessayer")=>{if(!Lt(t))return e;const{body:a}=t;return Array.isArray(a)&&a.length>0?a.map(n=>Object.values(n).join(" ")).join(" "):a instanceof Object&&Object.keys(a).length>0?Object.values(a).map(n=>Array.isArray(n)?n.join(" "):n).join(" "):e},Qs=async(t,e="image.jpg")=>{const n=await(await fetch(t)).blob();return new File([n],e,{type:n.type})};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const kt={SDK_VERSION:"${JSCORE_VERSION}"};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Q=function(t,e){if(!t)throw Mt(e)},Mt=function(t){return new Error("Firebase Database ("+kt.SDK_VERSION+") INTERNAL ASSERT FAILED: "+t)};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const We=function(t){const e=[];let a=0;for(let n=0;n<t.length;n++){let s=t.charCodeAt(n);s<128?e[a++]=s:s<2048?(e[a++]=s>>6|192,e[a++]=s&63|128):(s&64512)===55296&&n+1<t.length&&(t.charCodeAt(n+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++n)&1023),e[a++]=s>>18|240,e[a++]=s>>12&63|128,e[a++]=s>>6&63|128,e[a++]=s&63|128):(e[a++]=s>>12|224,e[a++]=s>>6&63|128,e[a++]=s&63|128)}return e},Ft=function(t){const e=[];let a=0,n=0;for(;a<t.length;){const s=t[a++];if(s<128)e[n++]=String.fromCharCode(s);else if(s>191&&s<224){const r=t[a++];e[n++]=String.fromCharCode((s&31)<<6|r&63)}else if(s>239&&s<365){const r=t[a++],i=t[a++],o=t[a++],c=((s&7)<<18|(r&63)<<12|(i&63)<<6|o&63)-65536;e[n++]=String.fromCharCode(55296+(c>>10)),e[n++]=String.fromCharCode(56320+(c&1023))}else{const r=t[a++],i=t[a++];e[n++]=String.fromCharCode((s&15)<<12|(r&63)<<6|i&63)}}return e.join("")},Nt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const a=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let s=0;s<t.length;s+=3){const r=t[s],i=s+1<t.length,o=i?t[s+1]:0,c=s+2<t.length,l=c?t[s+2]:0,f=r>>2,h=(r&3)<<4|o>>4;let u=(o&15)<<2|l>>6,E=l&63;c||(E=64,i||(u=64)),n.push(a[f],a[h],a[u],a[E])}return n.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(We(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):Ft(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const a=e?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let s=0;s<t.length;){const r=a[t.charAt(s++)],o=s<t.length?a[t.charAt(s)]:0;++s;const l=s<t.length?a[t.charAt(s)]:64;++s;const h=s<t.length?a[t.charAt(s)]:64;if(++s,r==null||o==null||l==null||h==null)throw new Pt;const u=r<<2|o>>4;if(n.push(u),l!==64){const E=o<<4&240|l>>2;if(n.push(E),h!==64){const I=l<<6&192|h;n.push(I)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}};class Pt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Bt=function(t){const e=We(t);return Nt.encodeByteArray(e,!0)},qe=function(t){return Bt(t).replace(/\./g,"")};function vt(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function ne(){try{return typeof indexedDB=="object"}catch{return!1}}function ze(){return new Promise((t,e)=>{try{let a=!0;const n="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(n);s.onsuccess=()=>{s.result.close(),a||self.indexedDB.deleteDatabase(n),t(!0)},s.onupgradeneeded=()=>{a=!1},s.onerror=()=>{e(s.error?.message||"")}}catch(a){e(a)}})}function $t(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Kt="FirebaseError";class A extends Error{constructor(e,a,n){super(a),this.code=e,this.customData=n,this.name=Kt,Object.setPrototypeOf(this,A.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,B.prototype.create)}}class B{constructor(e,a,n){this.service=e,this.serviceName=a,this.errors=n}create(e,...a){const n=a[0]||{},s=`${this.service}/${e}`,r=this.errors[e],i=r?Ht(r,n):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new A(s,o,n)}}function Ht(t,e){return t.replace(Vt,(a,n)=>{const s=e[n];return s!=null?String(s):`<${n}?>`})}const Vt=/\{\$([^}]+)}/g;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ut=1e3,xt=2,jt=4*60*60*1e3,Gt=.5;function K(t,e=Ut,a=xt){const n=e*Math.pow(a,t),s=Math.round(Gt*n*(Math.random()-.5)*2);return Math.min(jt,n+s)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function se(t){return t&&t._delegate?t._delegate:t}class w{constructor(e,a,n){this.name=e,this.instanceFactory=a,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var d;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(d||(d={}));const Wt={debug:d.DEBUG,verbose:d.VERBOSE,info:d.INFO,warn:d.WARN,error:d.ERROR,silent:d.SILENT},qt=d.INFO,zt={[d.DEBUG]:"log",[d.VERBOSE]:"log",[d.INFO]:"info",[d.WARN]:"warn",[d.ERROR]:"error"},Yt=(t,e,...a)=>{if(e<t.logLevel)return;const n=new Date().toISOString(),s=zt[e];if(s)console[s](`[${n}]  ${t.name}:`,...a);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class re{constructor(e){this.name=e,this._logLevel=qt,this._logHandler=Yt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in d))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Wt[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,d.DEBUG,...e),this._logHandler(this,d.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,d.VERBOSE,...e),this._logHandler(this,d.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,d.INFO,...e),this._logHandler(this,d.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,d.WARN,...e),this._logHandler(this,d.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,d.ERROR,...e),this._logHandler(this,d.ERROR,...e)}}const Xt=(t,e)=>e.some(a=>t instanceof a);let Ee,Ie;function Jt(){return Ee||(Ee=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Qt(){return Ie||(Ie=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Ye=new WeakMap,Z=new WeakMap,Xe=new WeakMap,x=new WeakMap,ie=new WeakMap;function Zt(t){const e=new Promise((a,n)=>{const s=()=>{t.removeEventListener("success",r),t.removeEventListener("error",i)},r=()=>{a(y(t.result)),s()},i=()=>{n(t.error),s()};t.addEventListener("success",r),t.addEventListener("error",i)});return e.then(a=>{a instanceof IDBCursor&&Ye.set(a,t)}).catch(()=>{}),ie.set(e,t),e}function ea(t){if(Z.has(t))return;const e=new Promise((a,n)=>{const s=()=>{t.removeEventListener("complete",r),t.removeEventListener("error",i),t.removeEventListener("abort",i)},r=()=>{a(),s()},i=()=>{n(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",r),t.addEventListener("error",i),t.addEventListener("abort",i)});Z.set(t,e)}let ee={get(t,e,a){if(t instanceof IDBTransaction){if(e==="done")return Z.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Xe.get(t);if(e==="store")return a.objectStoreNames[1]?void 0:a.objectStore(a.objectStoreNames[0])}return y(t[e])},set(t,e,a){return t[e]=a,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function ta(t){ee=t(ee)}function aa(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...a){const n=t.call(j(this),e,...a);return Xe.set(n,e.sort?e.sort():[e]),y(n)}:Qt().includes(t)?function(...e){return t.apply(j(this),e),y(Ye.get(this))}:function(...e){return y(t.apply(j(this),e))}}function na(t){return typeof t=="function"?aa(t):(t instanceof IDBTransaction&&ea(t),Xt(t,Jt())?new Proxy(t,ee):t)}function y(t){if(t instanceof IDBRequest)return Zt(t);if(x.has(t))return x.get(t);const e=na(t);return e!==t&&(x.set(t,e),ie.set(e,t)),e}const j=t=>ie.get(t);function Je(t,e,{blocked:a,upgrade:n,blocking:s,terminated:r}={}){const i=indexedDB.open(t,e),o=y(i);return n&&i.addEventListener("upgradeneeded",c=>{n(y(i.result),c.oldVersion,c.newVersion,y(i.transaction),c)}),a&&i.addEventListener("blocked",c=>a(c.oldVersion,c.newVersion,c)),o.then(c=>{r&&c.addEventListener("close",()=>r()),s&&c.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const sa=["get","getKey","getAll","getAllKeys","count"],ra=["put","add","delete","clear"],G=new Map;function be(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(G.get(e))return G.get(e);const a=e.replace(/FromIndex$/,""),n=e!==a,s=ra.includes(a);if(!(a in(n?IDBIndex:IDBObjectStore).prototype)||!(s||sa.includes(a)))return;const r=async function(i,...o){const c=this.transaction(i,s?"readwrite":"readonly");let l=c.store;return n&&(l=l.index(o.shift())),(await Promise.all([l[a](...o),s&&c.done]))[0]};return G.set(e,r),r}ta(t=>({...t,get:(e,a,n)=>be(e,a)||t.get(e,a,n),has:(e,a)=>!!be(e,a)||t.has(e,a)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ia{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(a=>{if(oa(a)){const n=a.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(a=>a).join(" ")}}function oa(t){return t.getComponent()?.type==="VERSION"}const te="@firebase/app",Se="0.14.4";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const _=new re("@firebase/app"),ca="@firebase/app-compat",la="@firebase/analytics-compat",ha="@firebase/analytics",da="@firebase/app-check-compat",ua="@firebase/app-check",fa="@firebase/auth",ga="@firebase/auth-compat",ma="@firebase/database",pa="@firebase/data-connect",Ca="@firebase/database-compat",_a="@firebase/functions",Ea="@firebase/functions-compat",Ia="@firebase/installations",ba="@firebase/installations-compat",Sa="@firebase/messaging",ya="@firebase/messaging-compat",wa="@firebase/performance",Ta="@firebase/performance-compat",Aa="@firebase/remote-config",Da="@firebase/remote-config-compat",Ra="@firebase/storage",Oa="@firebase/storage-compat",La="@firebase/firestore",ka="@firebase/ai",Ma="@firebase/firestore-compat",Fa="firebase",Na="12.4.0",Pa={[te]:"fire-core",[ca]:"fire-core-compat",[ha]:"fire-analytics",[la]:"fire-analytics-compat",[ua]:"fire-app-check",[da]:"fire-app-check-compat",[fa]:"fire-auth",[ga]:"fire-auth-compat",[ma]:"fire-rtdb",[pa]:"fire-data-connect",[Ca]:"fire-rtdb-compat",[_a]:"fire-fn",[Ea]:"fire-fn-compat",[Ia]:"fire-iid",[ba]:"fire-iid-compat",[Sa]:"fire-fcm",[ya]:"fire-fcm-compat",[wa]:"fire-perf",[Ta]:"fire-perf-compat",[Aa]:"fire-rc",[Da]:"fire-rc-compat",[Ra]:"fire-gcs",[Oa]:"fire-gcs-compat",[La]:"fire-fst",[Ma]:"fire-fst-compat",[ka]:"fire-vertex","fire-js":"fire-js",[Fa]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ba=new Map,va=new Map,ye=new Map;function we(t,e){try{t.container.addComponent(e)}catch(a){_.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,a)}}function T(t){const e=t.name;if(ye.has(e))return _.debug(`There were multiple attempts to register component ${e}.`),!1;ye.set(e,t);for(const a of Ba.values())we(a,t);for(const a of va.values())we(a,t);return!0}function Qe(t,e){const a=t.container.getProvider("heartbeat").getImmediate({optional:!0});return a&&a.triggerHeartbeat(),t.container.getProvider(e)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const $a={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},oe=new B("app","Firebase",$a);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Te=Na;function C(t,e,a){let n=Pa[t]??t;a&&(n+=`-${a}`);const s=n.match(/\s|\//),r=e.match(/\s|\//);if(s||r){const i=[`Unable to register library "${n}" with version "${e}":`];s&&i.push(`library name "${n}" contains illegal characters (whitespace or "/")`),s&&r&&i.push("and"),r&&i.push(`version name "${e}" contains illegal characters (whitespace or "/")`),_.warn(i.join(" "));return}T(new w(`${n}-version`,()=>({library:n,version:e}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ka="firebase-heartbeat-database",Ha=1,P="firebase-heartbeat-store";let W=null;function Ze(){return W||(W=Je(Ka,Ha,{upgrade:(t,e)=>{switch(e){case 0:try{t.createObjectStore(P)}catch(a){console.warn(a)}}}}).catch(t=>{throw oe.create("idb-open",{originalErrorMessage:t.message})})),W}async function Va(t){try{const a=(await Ze()).transaction(P),n=await a.objectStore(P).get(et(t));return await a.done,n}catch(e){if(e instanceof A)_.warn(e.message);else{const a=oe.create("idb-get",{originalErrorMessage:e?.message});_.warn(a.message)}}}async function Ae(t,e){try{const n=(await Ze()).transaction(P,"readwrite");await n.objectStore(P).put(e,et(t)),await n.done}catch(a){if(a instanceof A)_.warn(a.message);else{const n=oe.create("idb-set",{originalErrorMessage:a?.message});_.warn(n.message)}}}function et(t){return`${t.name}!${t.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ua=1024,xa=30;class ja{constructor(e){this.container=e,this._heartbeatsCache=null;const a=this.container.getProvider("app").getImmediate();this._storage=new Wa(a),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),n=De();if(this._heartbeatsCache?.heartbeats==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null)||this._heartbeatsCache.lastSentHeartbeatDate===n||this._heartbeatsCache.heartbeats.some(s=>s.date===n))return;if(this._heartbeatsCache.heartbeats.push({date:n,agent:a}),this._heartbeatsCache.heartbeats.length>xa){const s=qa(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(s,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(e){_.warn(e)}}async getHeartbeatsHeader(){try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null||this._heartbeatsCache.heartbeats.length===0)return"";const e=De(),{heartbeatsToSend:a,unsentEntries:n}=Ga(this._heartbeatsCache.heartbeats),s=qe(JSON.stringify({version:2,heartbeats:a}));return this._heartbeatsCache.lastSentHeartbeatDate=e,n.length>0?(this._heartbeatsCache.heartbeats=n,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(e){return _.warn(e),""}}}function De(){return new Date().toISOString().substring(0,10)}function Ga(t,e=Ua){const a=[];let n=t.slice();for(const s of t){const r=a.find(i=>i.agent===s.agent);if(r){if(r.dates.push(s.date),Re(a)>e){r.dates.pop();break}}else if(a.push({agent:s.agent,dates:[s.date]}),Re(a)>e){a.pop();break}n=n.slice(1)}return{heartbeatsToSend:a,unsentEntries:n}}class Wa{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ne()?ze().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const a=await Va(this.app);return a?.heartbeats?a:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){if(await this._canUseIndexedDBPromise){const n=await this.read();return Ae(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){if(await this._canUseIndexedDBPromise){const n=await this.read();return Ae(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:[...n.heartbeats,...e.heartbeats]})}else return}}function Re(t){return qe(JSON.stringify({version:2,heartbeats:t})).length}function qa(t){if(t.length===0)return-1;let e=0,a=t[0].date;for(let n=1;n<t.length;n++)t[n].date<a&&(a=t[n].date,e=n);return e}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function za(t){T(new w("platform-logger",e=>new ia(e),"PRIVATE")),T(new w("heartbeat",e=>new ja(e),"PRIVATE")),C(te,Se,t),C(te,Se,"esm2020"),C("fire-js","")}za("");const tt="@firebase/installations",ce="0.6.19";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const at=1e4,nt=`w:${ce}`,st="FIS_v2",Ya="https://firebaseinstallations.googleapis.com/v1",Xa=60*60*1e3,Ja="installations",Qa="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Za={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},O=new B(Ja,Qa,Za);function rt(t){return t instanceof A&&t.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function it({projectId:t}){return`${Ya}/projects/${t}/installations`}function ot(t){return{token:t.token,requestStatus:2,expiresIn:tn(t.expiresIn),creationTime:Date.now()}}async function ct(t,e){const n=(await e.json()).error;return O.create("request-failed",{requestName:t,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function lt({apiKey:t}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":t})}function en(t,{refreshToken:e}){const a=lt(t);return a.append("Authorization",an(e)),a}async function ht(t){const e=await t();return e.status>=500&&e.status<600?t():e}function tn(t){return Number(t.replace("s","000"))}function an(t){return`${st} ${t}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function nn({appConfig:t,heartbeatServiceProvider:e},{fid:a}){const n=it(t),s=lt(t),r=e.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:a,authVersion:st,appId:t.appId,sdkVersion:nt},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await ht(()=>fetch(n,o));if(c.ok){const l=await c.json();return{fid:l.fid||a,registrationStatus:2,refreshToken:l.refreshToken,authToken:ot(l.authToken)}}else throw await ct("Create Installation",c)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function dt(t){return new Promise(e=>{setTimeout(e,t)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function sn(t){return btoa(String.fromCharCode(...t)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const rn=/^[cdef][\w-]{21}$/,ae="";function on(){try{const t=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(t),t[0]=112+t[0]%16;const a=cn(t);return rn.test(a)?a:ae}catch{return ae}}function cn(t){return sn(t).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function V(t){return`${t.appName}!${t.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ut=new Map;function ft(t,e){const a=V(t);gt(a,e),ln(a,e)}function gt(t,e){const a=ut.get(t);if(a)for(const n of a)n(e)}function ln(t,e){const a=hn();a&&a.postMessage({key:t,fid:e}),dn()}let R=null;function hn(){return!R&&"BroadcastChannel"in self&&(R=new BroadcastChannel("[Firebase] FID Change"),R.onmessage=t=>{gt(t.data.key,t.data.fid)}),R}function dn(){ut.size===0&&R&&(R.close(),R=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const un="firebase-installations-database",fn=1,L="firebase-installations-store";let q=null;function le(){return q||(q=Je(un,fn,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(L)}}})),q}async function H(t,e){const a=V(t),s=(await le()).transaction(L,"readwrite"),r=s.objectStore(L),i=await r.get(a);return await r.put(e,a),await s.done,(!i||i.fid!==e.fid)&&ft(t,e.fid),e}async function mt(t){const e=V(t),n=(await le()).transaction(L,"readwrite");await n.objectStore(L).delete(e),await n.done}async function U(t,e){const a=V(t),s=(await le()).transaction(L,"readwrite"),r=s.objectStore(L),i=await r.get(a),o=e(i);return o===void 0?await r.delete(a):await r.put(o,a),await s.done,o&&(!i||i.fid!==o.fid)&&ft(t,o.fid),o}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function he(t){let e;const a=await U(t.appConfig,n=>{const s=gn(n),r=mn(t,s);return e=r.registrationPromise,r.installationEntry});return a.fid===ae?{installationEntry:await e}:{installationEntry:a,registrationPromise:e}}function gn(t){const e=t||{fid:on(),registrationStatus:0};return pt(e)}function mn(t,e){if(e.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(O.create("app-offline"));return{installationEntry:e,registrationPromise:s}}const a={fid:e.fid,registrationStatus:1,registrationTime:Date.now()},n=pn(t,a);return{installationEntry:a,registrationPromise:n}}else return e.registrationStatus===1?{installationEntry:e,registrationPromise:Cn(t)}:{installationEntry:e}}async function pn(t,e){try{const a=await nn(t,e);return H(t.appConfig,a)}catch(a){throw rt(a)&&a.customData.serverCode===409?await mt(t.appConfig):await H(t.appConfig,{fid:e.fid,registrationStatus:0}),a}}async function Cn(t){let e=await Oe(t.appConfig);for(;e.registrationStatus===1;)await dt(100),e=await Oe(t.appConfig);if(e.registrationStatus===0){const{installationEntry:a,registrationPromise:n}=await he(t);return n||a}return e}function Oe(t){return U(t,e=>{if(!e)throw O.create("installation-not-found");return pt(e)})}function pt(t){return _n(t)?{fid:t.fid,registrationStatus:0}:t}function _n(t){return t.registrationStatus===1&&t.registrationTime+at<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function En({appConfig:t,heartbeatServiceProvider:e},a){const n=In(t,a),s=en(t,a),r=e.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:nt,appId:t.appId}},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await ht(()=>fetch(n,o));if(c.ok){const l=await c.json();return ot(l)}else throw await ct("Generate Auth Token",c)}function In(t,{fid:e}){return`${it(t)}/${e}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function de(t,e=!1){let a;const n=await U(t.appConfig,r=>{if(!Ct(r))throw O.create("not-registered");const i=r.authToken;if(!e&&yn(i))return r;if(i.requestStatus===1)return a=bn(t,e),r;{if(!navigator.onLine)throw O.create("app-offline");const o=Tn(r);return a=Sn(t,o),o}});return a?await a:n.authToken}async function bn(t,e){let a=await Le(t.appConfig);for(;a.authToken.requestStatus===1;)await dt(100),a=await Le(t.appConfig);const n=a.authToken;return n.requestStatus===0?de(t,e):n}function Le(t){return U(t,e=>{if(!Ct(e))throw O.create("not-registered");const a=e.authToken;return An(a)?{...e,authToken:{requestStatus:0}}:e})}async function Sn(t,e){try{const a=await En(t,e),n={...e,authToken:a};return await H(t.appConfig,n),a}catch(a){if(rt(a)&&(a.customData.serverCode===401||a.customData.serverCode===404))await mt(t.appConfig);else{const n={...e,authToken:{requestStatus:0}};await H(t.appConfig,n)}throw a}}function Ct(t){return t!==void 0&&t.registrationStatus===2}function yn(t){return t.requestStatus===2&&!wn(t)}function wn(t){const e=Date.now();return e<t.creationTime||t.creationTime+t.expiresIn<e+Xa}function Tn(t){const e={requestStatus:1,requestTime:Date.now()};return{...t,authToken:e}}function An(t){return t.requestStatus===1&&t.requestTime+at<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Dn(t){const e=t,{installationEntry:a,registrationPromise:n}=await he(e);return n?n.catch(console.error):de(e).catch(console.error),a.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Rn(t,e=!1){const a=t;return await On(a),(await de(a,e)).token}async function On(t){const{registrationPromise:e}=await he(t);e&&await e}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ln(t){if(!t||!t.options)throw z("App Configuration");if(!t.name)throw z("App Name");const e=["projectId","apiKey","appId"];for(const a of e)if(!t.options[a])throw z(a);return{appName:t.name,projectId:t.options.projectId,apiKey:t.options.apiKey,appId:t.options.appId}}function z(t){return O.create("missing-app-config-values",{valueName:t})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const _t="installations",kn="installations-internal",Mn=t=>{const e=t.getProvider("app").getImmediate(),a=Ln(e),n=Qe(e,"heartbeat");return{app:e,appConfig:a,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},Fn=t=>{const e=t.getProvider("app").getImmediate(),a=Qe(e,_t).getImmediate();return{getId:()=>Dn(a),getToken:s=>Rn(a,s)}};function Nn(){T(new w(_t,Mn,"PUBLIC")),T(new w(kn,Fn,"PRIVATE"))}Nn();C(tt,ce);C(tt,ce,"esm2020");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ke="analytics",Pn="firebase_id",Bn="origin",vn=60*1e3,$n="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ue="https://www.googletagmanager.com/gtag/js";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const m=new re("@firebase/analytics");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Kn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},p=new B("analytics","Analytics",Kn);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Hn(t){if(!t.startsWith(ue)){const e=p.create("invalid-gtag-resource",{gtagURL:t});return m.warn(e.message),""}return t}function Et(t){return Promise.all(t.map(e=>e.catch(a=>a)))}function Vn(t,e){let a;return window.trustedTypes&&(a=window.trustedTypes.createPolicy(t,e)),a}function Un(t,e){const a=Vn("firebase-js-sdk-policy",{createScriptURL:Hn}),n=document.createElement("script"),s=`${ue}?l=${t}&id=${e}`;n.src=a?a?.createScriptURL(s):s,n.async=!0,document.head.appendChild(n)}function xn(t){let e=[];return Array.isArray(window[t])?e=window[t]:window[t]=e,e}async function jn(t,e,a,n,s,r){const i=n[s];try{if(i)await e[i];else{const c=(await Et(a)).find(l=>l.measurementId===s);c&&await e[c.appId]}}catch(o){m.error(o)}t("config",s,r)}async function Gn(t,e,a,n,s){try{let r=[];if(s&&s.send_to){let i=s.send_to;Array.isArray(i)||(i=[i]);const o=await Et(a);for(const c of i){const l=o.find(h=>h.measurementId===c),f=l&&e[l.appId];if(f)r.push(f);else{r=[];break}}}r.length===0&&(r=Object.values(e)),await Promise.all(r),t("event",n,s||{})}catch(r){m.error(r)}}function Wn(t,e,a,n){async function s(r,...i){try{if(r==="event"){const[o,c]=i;await Gn(t,e,a,o,c)}else if(r==="config"){const[o,c]=i;await jn(t,e,a,n,o,c)}else if(r==="consent"){const[o,c]=i;t("consent",o,c)}else if(r==="get"){const[o,c,l]=i;t("get",o,c,l)}else if(r==="set"){const[o]=i;t("set",o)}else t(r,...i)}catch(o){m.error(o)}}return s}function qn(t,e,a,n,s){let r=function(...i){window[n].push(arguments)};return window[s]&&typeof window[s]=="function"&&(r=window[s]),window[s]=Wn(r,t,e,a),{gtagCore:r,wrappedGtag:window[s]}}function zn(t){const e=window.document.getElementsByTagName("script");for(const a of Object.values(e))if(a.src&&a.src.includes(ue)&&a.src.includes(t))return a;return null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Yn=30,Xn=1e3;class Jn{constructor(e={},a=Xn){this.throttleMetadata=e,this.intervalMillis=a}getThrottleMetadata(e){return this.throttleMetadata[e]}setThrottleMetadata(e,a){this.throttleMetadata[e]=a}deleteThrottleMetadata(e){delete this.throttleMetadata[e]}}const It=new Jn;function Qn(t){return new Headers({Accept:"application/json","x-goog-api-key":t})}async function Zn(t){const{appId:e,apiKey:a}=t,n={method:"GET",headers:Qn(a)},s=$n.replace("{app-id}",e),r=await fetch(s,n);if(r.status!==200&&r.status!==304){let i="";try{const o=await r.json();o.error?.message&&(i=o.error.message)}catch{}throw p.create("config-fetch-failed",{httpStatus:r.status,responseMessage:i})}return r.json()}async function es(t,e=It,a){const{appId:n,apiKey:s,measurementId:r}=t.options;if(!n)throw p.create("no-app-id");if(!s){if(r)return{measurementId:r,appId:n};throw p.create("no-api-key")}const i=e.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new ns;return setTimeout(async()=>{o.abort()},vn),bt({appId:n,apiKey:s,measurementId:r},i,o,e)}async function bt(t,{throttleEndTimeMillis:e,backoffCount:a},n,s=It){const{appId:r,measurementId:i}=t;try{await ts(n,e)}catch(o){if(i)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${o?.message}]`),{appId:r,measurementId:i};throw o}try{const o=await Zn(t);return s.deleteThrottleMetadata(r),o}catch(o){const c=o;if(!as(c)){if(s.deleteThrottleMetadata(r),i)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${c?.message}]`),{appId:r,measurementId:i};throw o}const l=Number(c?.customData?.httpStatus)===503?K(a,s.intervalMillis,Yn):K(a,s.intervalMillis),f={throttleEndTimeMillis:Date.now()+l,backoffCount:a+1};return s.setThrottleMetadata(r,f),m.debug(`Calling attemptFetch again in ${l} millis`),bt(t,f,n,s)}}function ts(t,e){return new Promise((a,n)=>{const s=Math.max(e-Date.now(),0),r=setTimeout(a,s);t.addEventListener(()=>{clearTimeout(r),n(p.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function as(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class ns{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}async function ss(t,e,a,n,s){if(s&&s.global){t("event",a,n);return}else{const r=await e,i={...n,send_to:r};t("event",a,i)}}async function rs(t,e,a,n){if(n&&n.global){const s={};for(const r of Object.keys(a))s[`user_properties.${r}`]=a[r];return t("set",s),Promise.resolve()}else{const s=await e;t("config",s,{update:!0,user_properties:a})}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function is(){if(ne())try{await ze()}catch(t){return m.warn(p.create("indexeddb-unavailable",{errorInfo:t?.toString()}).message),!1}else return m.warn(p.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function os(t,e,a,n,s,r,i){const o=es(t);o.then(u=>{a[u.measurementId]=u.appId,t.options.measurementId&&u.measurementId!==t.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${t.options.measurementId}) does not match the measurement ID fetched from the server (${u.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(u=>m.error(u)),e.push(o);const c=is().then(u=>{if(u)return n.getId()}),[l,f]=await Promise.all([o,c]);zn(r)||Un(r,l.measurementId),s("js",new Date);const h=i?.config??{};return h[Bn]="firebase",h.update=!0,f!=null&&(h[Pn]=f),s("config",l.measurementId,h),l.measurementId}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class cs{constructor(e){this.app=e}_delete(){return delete M[this.app.options.appId],Promise.resolve()}}let M={},Me=[];const Fe={};let Y="dataLayer",ls="gtag",Ne,fe,Pe=!1;function hs(){const t=[];if(vt()&&t.push("This is a browser extension environment."),$t()||t.push("Cookies are not available."),t.length>0){const e=t.map((n,s)=>`(${s+1}) ${n}`).join(" "),a=p.create("invalid-analytics-context",{errorInfo:e});m.warn(a.message)}}function ds(t,e,a){hs();const n=t.options.appId;if(!n)throw p.create("no-app-id");if(!t.options.apiKey)if(t.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${t.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw p.create("no-api-key");if(M[n]!=null)throw p.create("already-exists",{id:n});if(!Pe){xn(Y);const{wrappedGtag:r,gtagCore:i}=qn(M,Me,Fe,Y,ls);fe=r,Ne=i,Pe=!0}return M[n]=os(t,Me,Fe,e,Ne,Y,a),new cs(t)}function us(t,e,a){t=se(t),rs(fe,M[t.app.options.appId],e,a).catch(n=>m.error(n))}function fs(t,e,a,n){t=se(t),ss(fe,M[t.app.options.appId],e,a,n).catch(s=>m.error(s))}const Be="@firebase/analytics",ve="0.10.19";function gs(){T(new w(ke,(e,{options:a})=>{const n=e.getProvider("app").getImmediate(),s=e.getProvider("installations-internal").getImmediate();return ds(n,s,a)},"PUBLIC")),T(new w("analytics-internal",t,"PRIVATE")),C(Be,ve),C(Be,ve,"esm2020");function t(e){try{const a=e.getProvider(ke).getImmediate();return{logEvent:(n,s,r)=>fs(a,n,s,r),setUserProperties:(n,s)=>us(a,n,s)}}catch(a){throw p.create("interop-component-reg-failed",{reason:a})}}}gs();const X="@firebase/remote-config",$e="0.7.0";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ms{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ps="remote-config",Ke=100;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Cs={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported.","stream-error":"The stream was not able to connect to the backend: {$originalErrorMessage}.","realtime-unavailable":"The Realtime service is unavailable: {$originalErrorMessage}","update-message-invalid":"The stream invalidation message was unparsable: {$originalErrorMessage}","update-not-fetched":"Unable to fetch the latest config: {$originalErrorMessage}"},g=new B("remoteconfig","Remote Config",Cs);function _s(t){const e=se(t);return e._initializePromise||(e._initializePromise=e._storageCache.loadFromStorage().then(()=>{e._isInitializationComplete=!0})),e._initializePromise}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Es{constructor(e,a,n,s){this.client=e,this.storage=a,this.storageCache=n,this.logger=s}isCachedDataFresh(e,a){if(!a)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-a,s=n<=e;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${e}. Is cache hit: ${s}.`),s}async fetch(e){const[a,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(e.cacheMaxAgeMillis,a))return n;e.eTag=n&&n.eTag;const s=await this.client.fetch(e),r=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&r.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(r),s}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Is(t=navigator){return t.languages&&t.languages[0]||t.language}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class bs{constructor(e,a,n,s,r,i){this.firebaseInstallations=e,this.sdkVersion=a,this.namespace=n,this.projectId=s,this.apiKey=r,this.appId=i}async fetch(e){const[a,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),r=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":e.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:a,app_instance_id_token:n,app_id:this.appId,language_code:Is(),custom_signals:e.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(r,c),f=new Promise((b,k)=>{e.signal.addEventListener(()=>{const me=new Error("The operation was aborted.");me.name="AbortError",k(me)})});let h;try{await Promise.race([l,f]),h=await l}catch(b){let k="fetch-client-network";throw b?.name==="AbortError"&&(k="fetch-timeout"),g.create(k,{originalErrorMessage:b?.message})}let u=h.status;const E=h.headers.get("ETag")||void 0;let I,D,F;if(h.status===200){let b;try{b=await h.json()}catch(k){throw g.create("fetch-client-parse",{originalErrorMessage:k?.message})}I=b.entries,D=b.state,F=b.templateVersion}if(D==="INSTANCE_STATE_UNSPECIFIED"?u=500:D==="NO_CHANGE"?u=304:(D==="NO_TEMPLATE"||D==="EMPTY_CONFIG")&&(I={}),u!==304&&u!==200)throw g.create("fetch-status",{httpStatus:u});return{status:u,eTag:E,config:I,templateVersion:F}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ss(t,e){return new Promise((a,n)=>{const s=Math.max(e-Date.now(),0),r=setTimeout(a,s);t.addEventListener(()=>{clearTimeout(r),n(g.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function ys(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class ws{constructor(e,a){this.client=e,this.storage=a}async fetch(e){const a=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(e,a)}async attemptFetch(e,{throttleEndTimeMillis:a,backoffCount:n}){await Ss(e.signal,a);try{const s=await this.client.fetch(e);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!ys(s))throw s;const r={throttleEndTimeMillis:Date.now()+K(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(r),this.attemptFetch(e,r)}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ts=60*1e3,As=12*60*60*1e3;class Ds{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(e,a,n,s,r,i){this.app=e,this._client=a,this._storageCache=n,this._storage=s,this._logger=r,this._realtimeHandler=i,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Ts,minimumFetchIntervalMillis:As},this.defaultConfig={}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $(t,e){const a=t.target.error||void 0;return g.create(e,{originalErrorMessage:a&&a?.message})}const S="app_namespace_store",Rs="firebase_remote_config",Os=1;function Ls(){return new Promise((t,e)=>{try{const a=indexedDB.open(Rs,Os);a.onerror=n=>{e($(n,"storage-open"))},a.onsuccess=n=>{t(n.target.result)},a.onupgradeneeded=n=>{const s=n.target.result;switch(n.oldVersion){case 0:s.createObjectStore(S,{keyPath:"compositeKey"})}}}catch(a){e(g.create("storage-open",{originalErrorMessage:a?.message}))}})}class St{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(e){return this.set("last_fetch_status",e)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(e){return this.set("last_successful_fetch_timestamp_millis",e)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(e){return this.set("last_successful_fetch_response",e)}getActiveConfig(){return this.get("active_config")}setActiveConfig(e){return this.set("active_config",e)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(e){return this.set("active_config_etag",e)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(e){return this.set("throttle_metadata",e)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}getRealtimeBackoffMetadata(){return this.get("realtime_backoff_metadata")}setRealtimeBackoffMetadata(e){return this.set("realtime_backoff_metadata",e)}getActiveConfigTemplateVersion(){return this.get("last_known_template_version")}setActiveConfigTemplateVersion(e){return this.set("last_known_template_version",e)}}class ks extends St{constructor(e,a,n,s=Ls()){super(),this.appId=e,this.appName=a,this.namespace=n,this.openDbPromise=s}async setCustomSignals(e){const n=(await this.openDbPromise).transaction([S],"readwrite"),s=await this.getWithTransaction("custom_signals",n),r=yt(e,s||{});return await this.setWithTransaction("custom_signals",r,n),r}async getWithTransaction(e,a){return new Promise((n,s)=>{const r=a.objectStore(S),i=this.createCompositeKey(e);try{const o=r.get(i);o.onerror=c=>{s($(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;n(l?l.value:void 0)}}catch(o){s(g.create("storage-get",{originalErrorMessage:o?.message}))}})}async setWithTransaction(e,a,n){return new Promise((s,r)=>{const i=n.objectStore(S),o=this.createCompositeKey(e);try{const c=i.put({compositeKey:o,value:a});c.onerror=l=>{r($(l,"storage-set"))},c.onsuccess=()=>{s()}}catch(c){r(g.create("storage-set",{originalErrorMessage:c?.message}))}})}async get(e){const n=(await this.openDbPromise).transaction([S],"readonly");return this.getWithTransaction(e,n)}async set(e,a){const s=(await this.openDbPromise).transaction([S],"readwrite");return this.setWithTransaction(e,a,s)}async delete(e){const a=await this.openDbPromise;return new Promise((n,s)=>{const i=a.transaction([S],"readwrite").objectStore(S),o=this.createCompositeKey(e);try{const c=i.delete(o);c.onerror=l=>{s($(l,"storage-delete"))},c.onsuccess=()=>{n()}}catch(c){s(g.create("storage-delete",{originalErrorMessage:c?.message}))}})}createCompositeKey(e){return[this.appId,this.appName,this.namespace,e].join()}}class Ms extends St{constructor(){super(...arguments),this.storage={}}async get(e){return Promise.resolve(this.storage[e])}async set(e,a){return this.storage[e]=a,Promise.resolve(void 0)}async delete(e){return this.storage[e]=void 0,Promise.resolve()}async setCustomSignals(e){const a=this.storage.custom_signals||{};return this.storage.custom_signals=yt(e,a),Promise.resolve(this.storage.custom_signals)}}function yt(t,e){const a={...e,...t},n=Object.fromEntries(Object.entries(a).filter(([s,r])=>r!==null).map(([s,r])=>typeof r=="number"?[s,r.toString()]:[s,r]));if(Object.keys(n).length>Ke)throw g.create("custom-signal-max-allowed-signals",{maxSignals:Ke});return n}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Fs{constructor(e){this.storage=e}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const e=this.storage.getLastFetchStatus(),a=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),s=this.storage.getCustomSignals(),r=await e;r&&(this.lastFetchStatus=r);const i=await a;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await n;o&&(this.activeConfig=o);const c=await s;c&&(this.customSignals=c)}setLastFetchStatus(e){return this.lastFetchStatus=e,this.storage.setLastFetchStatus(e)}setLastSuccessfulFetchTimestampMillis(e){return this.lastSuccessfulFetchTimestampMillis=e,this.storage.setLastSuccessfulFetchTimestampMillis(e)}setActiveConfig(e){return this.activeConfig=e,this.storage.setActiveConfig(e)}async setCustomSignals(e){this.customSignals=await this.storage.setCustomSignals(e)}}/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Ns{constructor(e){this.allowedEvents_=e,this.listeners_={},Q(Array.isArray(e)&&e.length>0,"Requires a non-empty array")}trigger(e,...a){if(Array.isArray(this.listeners_[e])){const n=[...this.listeners_[e]];for(let s=0;s<n.length;s++)n[s].callback.apply(n[s].context,a)}}on(e,a,n){this.validateEventType_(e),this.listeners_[e]=this.listeners_[e]||[],this.listeners_[e].push({callback:a,context:n});const s=this.getInitialEvent(e);s&&a.apply(n,s)}off(e,a,n){this.validateEventType_(e);const s=this.listeners_[e]||[];for(let r=0;r<s.length;r++)if(s[r].callback===a&&(!n||n===s[r].context)){s.splice(r,1);return}}validateEventType_(e){Q(this.allowedEvents_.find(a=>a===e),"Unknown event: "+e)}}/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ge extends Ns{static getInstance(){return new ge}constructor(){super(["visible"]);let e,a;typeof document<"u"&&typeof document.addEventListener<"u"&&(typeof document.hidden<"u"?(a="visibilitychange",e="hidden"):typeof document.mozHidden<"u"?(a="mozvisibilitychange",e="mozHidden"):typeof document.msHidden<"u"?(a="msvisibilitychange",e="msHidden"):typeof document.webkitHidden<"u"&&(a="webkitvisibilitychange",e="webkitHidden")),this.visible_=!0,a&&document.addEventListener(a,()=>{const n=!document[e];n!==this.visible_&&(this.visible_=n,this.trigger("visible",n))},!1)}getInitialEvent(e){return Q(e==="visible","Unknown event type: "+e),[this.visible_]}}/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ps="X-Goog-Api-Key",Bs="X-Goog-Firebase-Installations-Auth",J=8,He=3,Ve=-1,Ue=0,xe="featureDisabled",je="retryIntervalSeconds",Ge="latestTemplateVersionNumber";class vs{constructor(e,a,n,s,r,i,o,c,l,f){this.firebaseInstallations=e,this.storage=a,this.sdkVersion=n,this.namespace=s,this.projectId=r,this.apiKey=i,this.appId=o,this.logger=c,this.storageCache=l,this.cachingClient=f,this.observers=new Set,this.isConnectionActive=!1,this.isRealtimeDisabled=!1,this.httpRetriesRemaining=J,this.isInBackground=!1,this.decoder=new TextDecoder("utf-8"),this.isClosingConnection=!1,this.propagateError=h=>this.observers.forEach(u=>u.error?.(h)),this.isStatusCodeRetryable=h=>!h||[408,429,502,503,504].includes(h),this.setRetriesRemaining(),ge.getInstance().on("visible",this.onVisibilityChange,this)}async setRetriesRemaining(){const a=(await this.storage.getRealtimeBackoffMetadata())?.numFailedStreams||0;this.httpRetriesRemaining=Math.max(J-a,1)}async updateBackoffMetadataWithLastFailedStreamConnectionTime(e){const a=((await this.storage.getRealtimeBackoffMetadata())?.numFailedStreams||0)+1,n=K(a,6e4,2);await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:new Date(e.getTime()+n),numFailedStreams:a})}async updateBackoffMetadataWithRetryInterval(e){const a=Date.now(),n=e*1e3,s=new Date(a+n);await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:s,numFailedStreams:0}),await this.retryHttpConnectionWhenBackoffEnds()}async closeRealtimeHttpConnection(){if(!this.isClosingConnection){this.isClosingConnection=!0;try{this.reader&&await this.reader.cancel()}catch{this.logger.debug("Failed to cancel the reader, connection was lost.")}finally{this.reader=void 0}this.controller&&(await this.controller.abort(),this.controller=void 0),this.isClosingConnection=!1}}async resetRealtimeBackoff(){await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:new Date(-1),numFailedStreams:0})}resetRetryCount(){this.httpRetriesRemaining=J}async establishRealtimeConnection(e,a,n,s){const r=await this.storage.getActiveConfigEtag(),i=await this.storage.getActiveConfigTemplateVersion(),o={[Ps]:this.apiKey,[Bs]:n,"Content-Type":"application/json",Accept:"application/json","If-None-Match":r||"*","Content-Encoding":"gzip"},c={project:this.projectId,namespace:this.namespace,lastKnownVersionNumber:i,appId:this.appId,sdkVersion:this.sdkVersion,appInstanceId:a};return await fetch(e,{method:"POST",headers:o,body:JSON.stringify(c),signal:s})}getRealtimeUrl(){const a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfigrealtime.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:streamFetchInvalidations?key=${this.apiKey}`;return new URL(a)}async createRealtimeConnection(){const[e,a]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken(!1)]);this.controller=new AbortController;const n=this.getRealtimeUrl();return await this.establishRealtimeConnection(n,e,a,this.controller.signal)}async retryHttpConnectionWhenBackoffEnds(){let e=await this.storage.getRealtimeBackoffMetadata();e||(e={backoffEndTimeMillis:new Date(Ve),numFailedStreams:Ue});const a=new Date(e.backoffEndTimeMillis).getTime(),n=Date.now(),s=Math.max(0,a-n);await this.makeRealtimeHttpConnection(s)}setIsHttpConnectionRunning(e){this.isConnectionActive=e}checkAndSetHttpConnectionFlagIfNotRunning(){const e=this.canEstablishStreamConnection();return e&&this.setIsHttpConnectionRunning(!0),e}fetchResponseIsUpToDate(e,a){return e.config!=null&&e.templateVersion?e.templateVersion>=a:this.storageCache.getLastFetchStatus()==="success"}parseAndValidateConfigUpdateMessage(e){const a=e.indexOf("{"),n=e.indexOf("}",a);return a<0||n<0||a>=n?"":e.substring(a,n+1)}isEventListenersEmpty(){return this.observers.size===0}getRandomInt(e){return Math.floor(Math.random()*e)}executeAllListenerCallbacks(e){this.observers.forEach(a=>a.next(e))}getChangedParams(e,a){const n=new Set,s=new Set(Object.keys(e||{})),r=new Set(Object.keys(a||{}));for(const i of s)(!r.has(i)||e[i]!==a[i])&&n.add(i);for(const i of r)s.has(i)||n.add(i);return n}async fetchLatestConfig(e,a){const n=e-1,s=He-n,r=this.storageCache.getCustomSignals();r&&this.logger.debug(`Fetching config with custom signals: ${JSON.stringify(r)}`);const i=new ms;try{const o={cacheMaxAgeMillis:0,signal:i,customSignals:r,fetchType:"REALTIME",fetchAttempt:s},c=await this.cachingClient.fetch(o);let l=await this.storage.getActiveConfig();if(!this.fetchResponseIsUpToDate(c,a)){this.logger.debug("Fetched template version is the same as SDK's current version. Retrying fetch."),await this.autoFetch(n,a);return}if(c.config==null){this.logger.debug("The fetch succeeded, but the backend had no updates.");return}l==null&&(l={});const f=this.getChangedParams(c.config,l);if(f.size===0){this.logger.debug("Config was fetched, but no params changed.");return}const h={getUpdatedKeys(){return new Set(f)}};this.executeAllListenerCallbacks(h)}catch(o){const c=o instanceof Error?o.message:String(o),l=g.create("update-not-fetched",{originalErrorMessage:`Failed to auto-fetch config update: ${c}`});this.propagateError(l)}}async autoFetch(e,a){if(e===0){const r=g.create("update-not-fetched",{originalErrorMessage:"Unable to fetch the latest version of the template."});this.propagateError(r);return}const s=this.getRandomInt(4)*1e3;await new Promise(r=>setTimeout(r,s)),await this.fetchLatestConfig(e,a)}async handleNotifications(e){let a,n="";for(;;){const{done:s,value:r}=await e.read();if(s)break;if(a=this.decoder.decode(r,{stream:!0}),n+=a,a.includes("}")){if(n=this.parseAndValidateConfigUpdateMessage(n),n.length===0)continue;try{const i=JSON.parse(n);if(this.isEventListenersEmpty())break;if(xe in i&&i[xe]===!0){const o=g.create("realtime-unavailable",{originalErrorMessage:"The server is temporarily unavailable. Try again in a few minutes."});this.propagateError(o);break}if(Ge in i){const o=await this.storage.getActiveConfigTemplateVersion(),c=Number(i[Ge]);o&&c>o&&await this.autoFetch(He,c)}if(je in i){const o=Number(i[je]);await this.updateBackoffMetadataWithRetryInterval(o)}}catch(i){this.logger.debug("Unable to parse latest config update message.",i);const o=i instanceof Error?i.message:String(i);this.propagateError(g.create("update-message-invalid",{originalErrorMessage:o}))}n=""}}}async listenForNotifications(e){try{await this.handleNotifications(e)}catch{this.isInBackground||this.logger.debug("Real-time connection was closed due to an exception.")}}async prepareAndBeginRealtimeHttpStream(){if(!this.checkAndSetHttpConnectionFlagIfNotRunning())return;let e=await this.storage.getRealtimeBackoffMetadata();e||(e={backoffEndTimeMillis:new Date(Ve),numFailedStreams:Ue});const a=e.backoffEndTimeMillis.getTime();if(Date.now()<a){await this.retryHttpConnectionWhenBackoffEnds();return}let n,s;try{if(n=await this.createRealtimeConnection(),s=n.status,n.ok&&n.body){this.resetRetryCount(),await this.resetRealtimeBackoff();const r=n.body.getReader();this.reader=r,await this.listenForNotifications(r)}}catch(r){this.isInBackground?this.resetRetryCount():this.logger.debug("Exception connecting to real-time RC backend. Retrying the connection...:",r)}finally{await this.closeRealtimeHttpConnection(),this.setIsHttpConnectionRunning(!1);const r=!this.isInBackground&&(s===void 0||this.isStatusCodeRetryable(s));if(r&&await this.updateBackoffMetadataWithLastFailedStreamConnectionTime(new Date),r||n?.ok)await this.retryHttpConnectionWhenBackoffEnds();else{const i=`Unable to connect to the server. HTTP status code: ${s}`,o=g.create("stream-error",{originalErrorMessage:i});this.propagateError(o)}}}canEstablishStreamConnection(){const e=this.observers.size>0,a=!this.isRealtimeDisabled,n=!this.isConnectionActive,s=!this.isInBackground;return e&&a&&n&&s}async makeRealtimeHttpConnection(e){if(this.canEstablishStreamConnection()){if(this.httpRetriesRemaining>0)this.httpRetriesRemaining--,await new Promise(a=>setTimeout(a,e)),this.prepareAndBeginRealtimeHttpStream();else if(!this.isInBackground){const a=g.create("stream-error",{originalErrorMessage:"Unable to connect to the server. Check your connection and try again."});this.propagateError(a)}}}async beginRealtime(){this.observers.size>0&&await this.makeRealtimeHttpConnection(0)}addObserver(e){this.observers.add(e),this.beginRealtime()}removeObserver(e){this.observers.has(e)&&this.observers.delete(e)}async onVisibilityChange(e){this.isInBackground=!e,e?e&&await this.beginRealtime():await this.closeRealtimeHttpConnection()}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $s(){T(new w(ps,t,"PUBLIC").setMultipleInstances(!0)),C(X,$e),C(X,$e,"esm2020");function t(e,{options:a}){const n=e.getProvider("app").getImmediate(),s=e.getProvider("installations-internal").getImmediate(),{projectId:r,apiKey:i,appId:o}=n.options;if(!r)throw g.create("registration-project-id");if(!i)throw g.create("registration-api-key");if(!o)throw g.create("registration-app-id");const c=a?.templateId||"firebase",l=ne()?new ks(o,n.name,c):new Ms,f=new Fs(l),h=new re(X);h.logLevel=d.ERROR;const u=new bs(s,Te,c,r,i,o),E=new ws(u,l),I=new Es(E,l,f,h),D=new vs(s,l,Te,c,r,i,o,h,f,I),F=new Ds(n,I,f,l,h,D);return _s(F),F}}$s();const Ks=t=>Object.fromEntries(new URLSearchParams(t)),Hs=()=>{const t=Dt(),e=Ks(t.search);return"utm_campaign"in e&&"utm_medium"in e&&"utm_source"in e?{traffic_campaign:e.utm_campaign,traffic_medium:e.utm_medium,traffic_source:e.utm_source}:{}},Zs=()=>{const t=Hs();return{logEvent:N.useCallback((a,n)=>{},[t])}};var Vs=(t=>(t.CLICKED_BOOKING="hasClickedBooking",t.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",t.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",t.CLICKED_CONSULT_CGU="hasClickedConsultCGU",t.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",t.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",t.CLICKED_CREATE_VENUE="hasClickedCreateVenue",t.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",t.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",t.CLICKED_SAVE_VENUE="hasClickedSaveVenue",t.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",t.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",t.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",t.CLICKED_EDIT_PROFILE="hasClickedEditProfile",t.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",t.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",t.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",t.CLICKED_UNKNOWN_SIRET="hasClickedUnknownSiret",t.CLICKED_HELP_CENTER="hasClickedHelpCenter",t.CLICKED_HOME="hasClickedHome",t.CLICKED_LOGOUT="hasClickedLogout",t.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",t.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",t.CLICKED_VIEW_APP_HEADLINE_OFFER="hasClickedViewAppHeadlineOffer",t.CLICKED_OFFER="hasClickedOffer",t.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",t.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",t.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",t.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",t.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",t.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",t.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",t.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",t.CLICKED_PRO="hasClickedPro",t.CLICKED_REIMBURSEMENT="hasClickedReimbursement",t.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",t.CLICKED_STATS="hasClickedOffererStats",t.CLICKED_TICKET="hasClickedTicket",t.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",t.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",t.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",t.CLICKED_RESET_FILTERS="hasClickedResetFilter",t.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",t.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",t.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",t.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",t.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",t.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",t.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",t.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",t.FIRST_LOGIN="firstLogin",t.PAGE_VIEW="page_view",t.SIGNUP_FORM_ABORT="signupFormAbort",t.SIGNUP_FORM_SUCCESS="signupFormSuccess",t.TUTO_PAGE_VIEW="tutoPageView",t.DELETE_DRAFT_OFFER="DeleteDraftOffer",t.CLICKED_NO_VENUE="hasClickedNoVenue",t.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",t.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",t.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",t.CLICKED_ADD_IMAGE="hasClickedAddImage",t.DRAG_OR_SELECTED_IMAGE="hasDragOrSelectedImage",t.CLICKED_SAVE_IMAGE="hasClickedSaveImage",t.CLICKED_DELETE_STOCK="hasClickedDeleteStock",t.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",t.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",t.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",t.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",t.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",t.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",t.EXTRA_PRO_DATA="extra_pro_data",t.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",t.CLICKED_CONSULT_HELP="hasClickedConsultHelp",t.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",t.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",t.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",t.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",t.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",t.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",t.OFFER_FORM_VIDEO_URL_ERROR="videoUrlError",t))(Vs||{});export{Vs as E,Ce as I,_e as S,Js as a,Qs as g,Zs as u};
