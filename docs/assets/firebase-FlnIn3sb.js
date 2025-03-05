import{r as re}from"./index-ClcD9ViR.js";import"./config-BdqymTTq.js";import{b as Kt}from"./index-C3LhMar3.js";/**
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
 */const Ge=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let s=e.charCodeAt(r);s<128?t[n++]=s:s<2048?(t[n++]=s>>6|192,t[n++]=s&63|128):(s&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(s=65536+((s&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=s>>18|240,t[n++]=s>>12&63|128,t[n++]=s>>6&63|128,t[n++]=s&63|128):(t[n++]=s>>12|224,t[n++]=s>>6&63|128,t[n++]=s&63|128)}return t},Gt=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const s=e[n++];if(s<128)t[r++]=String.fromCharCode(s);else if(s>191&&s<224){const a=e[n++];t[r++]=String.fromCharCode((s&31)<<6|a&63)}else if(s>239&&s<365){const a=e[n++],i=e[n++],o=e[n++],c=((s&7)<<18|(a&63)<<12|(i&63)<<6|o&63)-65536;t[r++]=String.fromCharCode(55296+(c>>10)),t[r++]=String.fromCharCode(56320+(c&1023))}else{const a=e[n++],i=e[n++];t[r++]=String.fromCharCode((s&15)<<12|(a&63)<<6|i&63)}}return t.join("")},zt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let s=0;s<e.length;s+=3){const a=e[s],i=s+1<e.length,o=i?e[s+1]:0,c=s+2<e.length,l=c?e[s+2]:0,h=a>>2,d=(a&3)<<4|o>>4;let f=(o&15)<<2|l>>6,g=l&63;c||(g=64,i||(f=64)),r.push(n[h],n[d],n[f],n[g])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Ge(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):Gt(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let s=0;s<e.length;){const a=n[e.charAt(s++)],o=s<e.length?n[e.charAt(s)]:0;++s;const l=s<e.length?n[e.charAt(s)]:64;++s;const d=s<e.length?n[e.charAt(s)]:64;if(++s,a==null||o==null||l==null||d==null)throw new Yt;const f=a<<2|o>>4;if(r.push(f),l!==64){const g=o<<4&240|l>>2;if(r.push(g),d!==64){const S=l<<6&192|d;r.push(S)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class Yt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Jt=function(e){const t=Ge(e);return zt.encodeByteArray(t,!0)},ze=function(e){return Jt(e).replace(/\./g,"")};function Xt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function Ye(){try{return typeof indexedDB=="object"}catch{return!1}}function Je(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(r);s.onsuccess=()=>{s.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},s.onupgradeneeded=()=>{n=!1},s.onerror=()=>{var a;t(((a=s.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){t(n)}})}function Qt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const Zt="FirebaseError";let N=class Xe extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=Zt,Object.setPrototypeOf(this,Xe.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,x.prototype.create)}},x=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},s=`${this.service}/${t}`,a=this.errors[t],i=a?en(a,r):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new N(s,o,r)}};function en(e,t){return e.replace(tn,(n,r)=>{const s=t[r];return s!=null?String(s):`<${r}?>`})}const tn=/\{\$([^}]+)}/g;/**
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
 */const nn=1e3,rn=2,sn=4*60*60*1e3,an=.5;function Ee(e,t=nn,n=rn){const r=t*Math.pow(n,e),s=Math.round(an*r*(Math.random()-.5)*2);return Math.min(sn,r+s)}/**
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
 */function on(e){return e&&e._delegate?e._delegate:e}let $=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const cn={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},ln=u.INFO,un={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},hn=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),s=un[t];if(s)console[s](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class le{constructor(t){this.name=t,this._logLevel=ln,this._logHandler=hn,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?cn[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const dn=(e,t)=>t.some(n=>e instanceof n);let _e,Ae;function fn(){return _e||(_e=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function gn(){return Ae||(Ae=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Qe=new WeakMap,se=new WeakMap,Ze=new WeakMap,G=new WeakMap,ue=new WeakMap;function pn(e){const t=new Promise((n,r)=>{const s=()=>{e.removeEventListener("success",a),e.removeEventListener("error",i)},a=()=>{n(A(e.result)),s()},i=()=>{r(e.error),s()};e.addEventListener("success",a),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&Qe.set(n,e)}).catch(()=>{}),ue.set(t,e),t}function mn(e){if(se.has(e))return;const t=new Promise((n,r)=>{const s=()=>{e.removeEventListener("complete",a),e.removeEventListener("error",i),e.removeEventListener("abort",i)},a=()=>{n(),s()},i=()=>{r(e.error||new DOMException("AbortError","AbortError")),s()};e.addEventListener("complete",a),e.addEventListener("error",i),e.addEventListener("abort",i)});se.set(e,t)}let ae={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return se.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ze.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return A(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function bn(e){ae=e(ae)}function wn(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(z(this),t,...n);return Ze.set(r,t.sort?t.sort():[t]),A(r)}:gn().includes(e)?function(...t){return e.apply(z(this),t),A(Qe.get(this))}:function(...t){return A(e.apply(z(this),t))}}function yn(e){return typeof e=="function"?wn(e):(e instanceof IDBTransaction&&mn(e),dn(e,fn())?new Proxy(e,ae):e)}function A(e){if(e instanceof IDBRequest)return pn(e);if(G.has(e))return G.get(e);const t=yn(e);return t!==e&&(G.set(e,t),ue.set(t,e)),t}const z=e=>ue.get(e);function he(e,t,{blocked:n,upgrade:r,blocking:s,terminated:a}={}){const i=indexedDB.open(e,t),o=A(i);return r&&i.addEventListener("upgradeneeded",c=>{r(A(i.result),c.oldVersion,c.newVersion,A(i.transaction),c)}),n&&i.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),o.then(c=>{a&&c.addEventListener("close",()=>a()),s&&c.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const In=["get","getKey","getAll","getAllKeys","count"],Tn=["put","add","delete","clear"],Y=new Map;function Ce(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(Y.get(t))return Y.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,s=Tn.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(s||In.includes(n)))return;const a=async function(i,...o){const c=this.transaction(i,s?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(o.shift())),(await Promise.all([l[n](...o),s&&c.done]))[0]};return Y.set(t,a),a}bn(e=>({...e,get:(t,n,r)=>Ce(t,n)||e.get(t,n,r),has:(t,n)=>!!Ce(t,n)||e.has(t,n)}));/**
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
 */class Sn{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(En(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function En(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const ie="@firebase/app",ve="0.11.2";/**
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
 */const T=new le("@firebase/app"),_n="@firebase/app-compat",An="@firebase/analytics-compat",Cn="@firebase/analytics",vn="@firebase/app-check-compat",$n="@firebase/app-check",Mn="@firebase/auth",Rn="@firebase/auth-compat",Dn="@firebase/database",Pn="@firebase/data-connect",On="@firebase/database-compat",Fn="@firebase/functions",kn="@firebase/functions-compat",Nn="@firebase/installations",Bn="@firebase/installations-compat",Ln="@firebase/messaging",jn="@firebase/messaging-compat",xn="@firebase/performance",Hn="@firebase/performance-compat",Vn="@firebase/remote-config",Un="@firebase/remote-config-compat",qn="@firebase/storage",Wn="@firebase/storage-compat",Kn="@firebase/firestore",Gn="@firebase/vertexai",zn="@firebase/firestore-compat",Yn="firebase",Jn="11.4.0",Xn={[ie]:"fire-core",[_n]:"fire-core-compat",[Cn]:"fire-analytics",[An]:"fire-analytics-compat",[$n]:"fire-app-check",[vn]:"fire-app-check-compat",[Mn]:"fire-auth",[Rn]:"fire-auth-compat",[Dn]:"fire-rtdb",[Pn]:"fire-data-connect",[On]:"fire-rtdb-compat",[Fn]:"fire-fn",[kn]:"fire-fn-compat",[Nn]:"fire-iid",[Bn]:"fire-iid-compat",[Ln]:"fire-fcm",[jn]:"fire-fcm-compat",[xn]:"fire-perf",[Hn]:"fire-perf-compat",[Vn]:"fire-rc",[Un]:"fire-rc-compat",[qn]:"fire-gcs",[Wn]:"fire-gcs-compat",[Kn]:"fire-fst",[zn]:"fire-fst-compat",[Gn]:"fire-vertex","fire-js":"fire-js",[Yn]:"fire-js-all"};/**
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
 */const Qn=new Map,Zn=new Map,$e=new Map;function Me(e,t){try{e.container.addComponent(t)}catch(n){T.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function I(e){const t=e.name;if($e.has(t))return T.debug(`There were multiple attempts to register component ${t}.`),!1;$e.set(t,e);for(const n of Qn.values())Me(n,e);for(const n of Zn.values())Me(n,e);return!0}function H(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const er={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},de=new x("app","Firebase",er);/**
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
 */const tr=Jn;function y(e,t,n){var r;let s=(r=Xn[e])!==null&&r!==void 0?r:e;n&&(s+=`-${n}`);const a=s.match(/\s|\//),i=t.match(/\s|\//);if(a||i){const o=[`Unable to register library "${s}" with version "${t}":`];a&&o.push(`library name "${s}" contains illegal characters (whitespace or "/")`),a&&i&&o.push("and"),i&&o.push(`version name "${t}" contains illegal characters (whitespace or "/")`),T.warn(o.join(" "));return}I(new $(`${s}-version`,()=>({library:s,version:t}),"VERSION"))}/**
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
 */const nr="firebase-heartbeat-database",rr=1,k="firebase-heartbeat-store";let J=null;function et(){return J||(J=he(nr,rr,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(k)}catch(n){console.warn(n)}}}}).catch(e=>{throw de.create("idb-open",{originalErrorMessage:e.message})})),J}async function sr(e){try{const n=(await et()).transaction(k),r=await n.objectStore(k).get(tt(e));return await n.done,r}catch(t){if(t instanceof N)T.warn(t.message);else{const n=de.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});T.warn(n.message)}}}async function Re(e,t){try{const r=(await et()).transaction(k,"readwrite");await r.objectStore(k).put(t,tt(e)),await r.done}catch(n){if(n instanceof N)T.warn(n.message);else{const r=de.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});T.warn(r.message)}}}function tt(e){return`${e.name}!${e.options.appId}`}/**
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
 */const ar=1024,ir=30;class or{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new lr(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;try{const s=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),a=De();if(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===a||this._heartbeatsCache.heartbeats.some(i=>i.date===a))return;if(this._heartbeatsCache.heartbeats.push({date:a,agent:s}),this._heartbeatsCache.heartbeats.length>ir){const i=ur(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(i,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(r){T.warn(r)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=De(),{heartbeatsToSend:r,unsentEntries:s}=cr(this._heartbeatsCache.heartbeats),a=ze(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,s.length>0?(this._heartbeatsCache.heartbeats=s,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),a}catch(n){return T.warn(n),""}}}function De(){return new Date().toISOString().substring(0,10)}function cr(e,t=ar){const n=[];let r=e.slice();for(const s of e){const a=n.find(i=>i.agent===s.agent);if(a){if(a.dates.push(s.date),Pe(n)>t){a.dates.pop();break}}else if(n.push({agent:s.agent,dates:[s.date]}),Pe(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class lr{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Ye()?Je().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await sr(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Re(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const s=await this.read();return Re(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...t.heartbeats]})}else return}}function Pe(e){return ze(JSON.stringify({version:2,heartbeats:e})).length}function ur(e){if(e.length===0)return-1;let t=0,n=e[0].date;for(let r=1;r<e.length;r++)e[r].date<n&&(n=e[r].date,t=r);return t}/**
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
 */function hr(e){I(new $("platform-logger",t=>new Sn(t),"PRIVATE")),I(new $("heartbeat",t=>new or(t),"PRIVATE")),y(ie,ve,e),y(ie,ve,"esm2017"),y("fire-js","")}hr("");const nt="@firebase/installations",fe="0.6.13";/**
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
 */const rt=1e4,st=`w:${fe}`,at="FIS_v2",dr="https://firebaseinstallations.googleapis.com/v1",fr=60*60*1e3,gr="installations",pr="Installations";/**
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
 */const mr={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},M=new x(gr,pr,mr);function it(e){return e instanceof N&&e.code.includes("request-failed")}/**
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
 */function ot({projectId:e}){return`${dr}/projects/${e}/installations`}function ct(e){return{token:e.token,requestStatus:2,expiresIn:wr(e.expiresIn),creationTime:Date.now()}}async function lt(e,t){const r=(await t.json()).error;return M.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function ut({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function br(e,{refreshToken:t}){const n=ut(e);return n.append("Authorization",yr(t)),n}async function ht(e){const t=await e();return t.status>=500&&t.status<600?e():t}function wr(e){return Number(e.replace("s","000"))}function yr(e){return`${at} ${e}`}/**
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
 */async function Ir({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=ot(e),s=ut(e),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:n,authVersion:at,appId:e.appId,sdkVersion:st},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await ht(()=>fetch(r,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:ct(l.authToken)}}else throw await lt("Create Installation",c)}/**
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
 */function dt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Tr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Sr=/^[cdef][\w-]{21}$/,oe="";function Er(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=_r(e);return Sr.test(n)?n:oe}catch{return oe}}function _r(e){return Tr(e).substr(0,22)}/**
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
 */function V(e){return`${e.appName}!${e.appId}`}/**
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
 */const ft=new Map;function gt(e,t){const n=V(e);pt(n,t),Ar(n,t)}function pt(e,t){const n=ft.get(e);if(n)for(const r of n)r(t)}function Ar(e,t){const n=Cr();n&&n.postMessage({key:e,fid:t}),vr()}let C=null;function Cr(){return!C&&"BroadcastChannel"in self&&(C=new BroadcastChannel("[Firebase] FID Change"),C.onmessage=e=>{pt(e.data.key,e.data.fid)}),C}function vr(){ft.size===0&&C&&(C.close(),C=null)}/**
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
 */const $r="firebase-installations-database",Mr=1,R="firebase-installations-store";let X=null;function ge(){return X||(X=he($r,Mr,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(R)}}})),X}async function L(e,t){const n=V(e),s=(await ge()).transaction(R,"readwrite"),a=s.objectStore(R),i=await a.get(n);return await a.put(t,n),await s.done,(!i||i.fid!==t.fid)&&gt(e,t.fid),t}async function mt(e){const t=V(e),r=(await ge()).transaction(R,"readwrite");await r.objectStore(R).delete(t),await r.done}async function U(e,t){const n=V(e),s=(await ge()).transaction(R,"readwrite"),a=s.objectStore(R),i=await a.get(n),o=t(i);return o===void 0?await a.delete(n):await a.put(o,n),await s.done,o&&(!i||i.fid!==o.fid)&&gt(e,o.fid),o}/**
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
 */async function pe(e){let t;const n=await U(e.appConfig,r=>{const s=Rr(r),a=Dr(e,s);return t=a.registrationPromise,a.installationEntry});return n.fid===oe?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function Rr(e){const t=e||{fid:Er(),registrationStatus:0};return bt(t)}function Dr(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(M.create("app-offline"));return{installationEntry:t,registrationPromise:s}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=Pr(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:Or(e)}:{installationEntry:t}}async function Pr(e,t){try{const n=await Ir(e,t);return L(e.appConfig,n)}catch(n){throw it(n)&&n.customData.serverCode===409?await mt(e.appConfig):await L(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function Or(e){let t=await Oe(e.appConfig);for(;t.registrationStatus===1;)await dt(100),t=await Oe(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await pe(e);return r||n}return t}function Oe(e){return U(e,t=>{if(!t)throw M.create("installation-not-found");return bt(t)})}function bt(e){return Fr(e)?{fid:e.fid,registrationStatus:0}:e}function Fr(e){return e.registrationStatus===1&&e.registrationTime+rt<Date.now()}/**
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
 */async function kr({appConfig:e,heartbeatServiceProvider:t},n){const r=Nr(e,n),s=br(e,n),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:st,appId:e.appId}},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await ht(()=>fetch(r,o));if(c.ok){const l=await c.json();return ct(l)}else throw await lt("Generate Auth Token",c)}function Nr(e,{fid:t}){return`${ot(e)}/${t}/authTokens:generate`}/**
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
 */async function me(e,t=!1){let n;const r=await U(e.appConfig,a=>{if(!wt(a))throw M.create("not-registered");const i=a.authToken;if(!t&&jr(i))return a;if(i.requestStatus===1)return n=Br(e,t),a;{if(!navigator.onLine)throw M.create("app-offline");const o=Hr(a);return n=Lr(e,o),o}});return n?await n:r.authToken}async function Br(e,t){let n=await Fe(e.appConfig);for(;n.authToken.requestStatus===1;)await dt(100),n=await Fe(e.appConfig);const r=n.authToken;return r.requestStatus===0?me(e,t):r}function Fe(e){return U(e,t=>{if(!wt(t))throw M.create("not-registered");const n=t.authToken;return Vr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Lr(e,t){try{const n=await kr(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await L(e.appConfig,r),n}catch(n){if(it(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await mt(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await L(e.appConfig,r)}throw n}}function wt(e){return e!==void 0&&e.registrationStatus===2}function jr(e){return e.requestStatus===2&&!xr(e)}function xr(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+fr}function Hr(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function Vr(e){return e.requestStatus===1&&e.requestTime+rt<Date.now()}/**
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
 */async function Ur(e){const t=e,{installationEntry:n,registrationPromise:r}=await pe(t);return r?r.catch(console.error):me(t).catch(console.error),n.fid}/**
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
 */async function qr(e,t=!1){const n=e;return await Wr(n),(await me(n,t)).token}async function Wr(e){const{registrationPromise:t}=await pe(e);t&&await t}/**
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
 */function Kr(e){if(!e||!e.options)throw Q("App Configuration");if(!e.name)throw Q("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw Q(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function Q(e){return M.create("missing-app-config-values",{valueName:e})}/**
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
 */const yt="installations",Gr="installations-internal",zr=e=>{const t=e.getProvider("app").getImmediate(),n=Kr(t),r=H(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Yr=e=>{const t=e.getProvider("app").getImmediate(),n=H(t,yt).getImmediate();return{getId:()=>Ur(n),getToken:s=>qr(n,s)}};function Jr(){I(new $(yt,zr,"PUBLIC")),I(new $(Gr,Yr,"PRIVATE"))}Jr();y(nt,fe);y(nt,fe,"esm2017");/**
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
 */const ke="analytics",Xr="firebase_id",Qr="origin",Zr=60*1e3,es="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",be="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new le("@firebase/analytics");/**
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
 */const ts={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},b=new x("analytics","Analytics",ts);/**
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
 */function ns(e){if(!e.startsWith(be)){const t=b.create("invalid-gtag-resource",{gtagURL:e});return m.warn(t.message),""}return e}function It(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function rs(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function ss(e,t){const n=rs("firebase-js-sdk-policy",{createScriptURL:ns}),r=document.createElement("script"),s=`${be}?l=${e}&id=${t}`;r.src=n?n==null?void 0:n.createScriptURL(s):s,r.async=!0,document.head.appendChild(r)}function as(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function is(e,t,n,r,s,a){const i=r[s];try{if(i)await t[i];else{const c=(await It(n)).find(l=>l.measurementId===s);c&&await t[c.appId]}}catch(o){m.error(o)}e("config",s,a)}async function os(e,t,n,r,s){try{let a=[];if(s&&s.send_to){let i=s.send_to;Array.isArray(i)||(i=[i]);const o=await It(n);for(const c of i){const l=o.find(d=>d.measurementId===c),h=l&&t[l.appId];if(h)a.push(h);else{a=[];break}}}a.length===0&&(a=Object.values(t)),await Promise.all(a),e("event",r,s||{})}catch(a){m.error(a)}}function cs(e,t,n,r){async function s(a,...i){try{if(a==="event"){const[o,c]=i;await os(e,t,n,o,c)}else if(a==="config"){const[o,c]=i;await is(e,t,n,r,o,c)}else if(a==="consent"){const[o,c]=i;e("consent",o,c)}else if(a==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(a==="set"){const[o]=i;e("set",o)}else e(a,...i)}catch(o){m.error(o)}}return s}function ls(e,t,n,r,s){let a=function(...i){window[r].push(arguments)};return window[s]&&typeof window[s]=="function"&&(a=window[s]),window[s]=cs(a,e,t,n),{gtagCore:a,wrappedGtag:window[s]}}function us(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(be)&&n.src.includes(e))return n;return null}/**
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
 */const hs=30,ds=1e3;class fs{constructor(t={},n=ds){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const Tt=new fs;function gs(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function ps(e){var t;const{appId:n,apiKey:r}=e,s={method:"GET",headers:gs(r)},a=es.replace("{app-id}",n),i=await fetch(a,s);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((t=c.error)===null||t===void 0)&&t.message&&(o=c.error.message)}catch{}throw b.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function ms(e,t=Tt,n){const{appId:r,apiKey:s,measurementId:a}=e.options;if(!r)throw b.create("no-app-id");if(!s){if(a)return{measurementId:a,appId:r};throw b.create("no-api-key")}const i=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new ys;return setTimeout(async()=>{o.abort()},Zr),St({appId:r,apiKey:s,measurementId:a},i,o,t)}async function St(e,{throttleEndTimeMillis:t,backoffCount:n},r,s=Tt){var a;const{appId:i,measurementId:o}=e;try{await bs(r,t)}catch(c){if(o)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await ps(e);return s.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!ws(l)){if(s.deleteThrottleMetadata(i),o)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const h=Number((a=l==null?void 0:l.customData)===null||a===void 0?void 0:a.httpStatus)===503?Ee(n,s.intervalMillis,hs):Ee(n,s.intervalMillis),d={throttleEndTimeMillis:Date.now()+h,backoffCount:n+1};return s.setThrottleMetadata(i,d),m.debug(`Calling attemptFetch again in ${h} millis`),St(e,d,r,s)}}function bs(e,t){return new Promise((n,r)=>{const s=Math.max(t-Date.now(),0),a=setTimeout(n,s);e.addEventListener(()=>{clearTimeout(a),r(b.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function ws(e){if(!(e instanceof N)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ys{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Is(e,t,n,r,s){if(s&&s.global){e("event",n,r);return}else{const a=await t,i=Object.assign(Object.assign({},r),{send_to:a});e("event",n,i)}}/**
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
 */async function Ts(){if(Ye())try{await Je()}catch(e){return m.warn(b.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(b.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Ss(e,t,n,r,s,a,i){var o;const c=ms(e);c.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),t.push(c);const l=Ts().then(g=>{if(g)return r.getId()}),[h,d]=await Promise.all([c,l]);us(a)||ss(a,h.measurementId),s("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[Qr]="firebase",f.update=!0,d!=null&&(f[Xr]=d),s("config",h.measurementId,f),h.measurementId}/**
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
 */class Es{constructor(t){this.app=t}_delete(){return delete F[this.app.options.appId],Promise.resolve()}}let F={},Ne=[];const Be={};let Z="dataLayer",_s="gtag",Le,Et,je=!1;function As(){const e=[];if(Xt()&&e.push("This is a browser extension environment."),Qt()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,s)=>`(${s+1}) ${r}`).join(" "),n=b.create("invalid-analytics-context",{errorInfo:t});m.warn(n.message)}}function Cs(e,t,n){As();const r=e.options.appId;if(!r)throw b.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw b.create("no-api-key");if(F[r]!=null)throw b.create("already-exists",{id:r});if(!je){as(Z);const{wrappedGtag:a,gtagCore:i}=ls(F,Ne,Be,Z,_s);Et=a,Le=i,je=!0}return F[r]=Ss(e,Ne,Be,t,Le,Z,n),new Es(e)}function vs(e,t,n,r){e=on(e),Is(Et,F[e.app.options.appId],t,n,r).catch(s=>m.error(s))}const xe="@firebase/analytics",He="0.10.12";function $s(){I(new $(ke,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();return Cs(r,s,n)},"PUBLIC")),I(new $("analytics-internal",e,"PRIVATE")),y(xe,He),y(xe,He,"esm2017");function e(t){try{const n=t.getProvider(ke).getImmediate();return{logEvent:(r,s,a)=>vs(n,r,s,a)}}catch(n){throw b.create("interop-component-reg-failed",{reason:n})}}}$s();function Ms(){try{return typeof indexedDB=="object"}catch{return!1}}/**
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
 */const Rs="FirebaseError";let _t=class At extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=Rs,Object.setPrototypeOf(this,At.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,Ct.prototype.create)}},Ct=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},s=`${this.service}/${t}`,a=this.errors[t],i=a?Ds(a,r):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new _t(s,o,r)}};function Ds(e,t){return e.replace(Ps,(n,r)=>{const s=t[r];return s!=null?String(s):`<${r}?>`})}const Ps=/\{\$([^}]+)}/g;/**
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
 */const Os=1e3,Fs=2,ks=4*60*60*1e3,Ns=.5;function Bs(e,t=Os,n=Fs){const r=t*Math.pow(n,e),s=Math.round(Ns*r*(Math.random()-.5)*2);return Math.min(ks,r+s)}/**
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
 */function Ls(e){return e&&e._delegate?e._delegate:e}let js=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */const xs="FirebaseError";class q extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=xs,Object.setPrototypeOf(this,q.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,vt.prototype.create)}}class vt{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},s=`${this.service}/${t}`,a=this.errors[t],i=a?Hs(a,r):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new q(s,o,r)}}function Hs(e,t){return e.replace(Vs,(n,r)=>{const s=t[r];return s!=null?String(s):`<${r}?>`})}const Vs=/\{\$([^}]+)}/g;class Ve{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}const $t="@firebase/installations",we="0.6.12";/**
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
 */const Mt=1e4,Rt=`w:${we}`,Dt="FIS_v2",Us="https://firebaseinstallations.googleapis.com/v1",qs=60*60*1e3,Ws="installations",Ks="Installations";/**
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
 */const Gs={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},D=new vt(Ws,Ks,Gs);function Pt(e){return e instanceof q&&e.code.includes("request-failed")}/**
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
 */function Ot({projectId:e}){return`${Us}/projects/${e}/installations`}function Ft(e){return{token:e.token,requestStatus:2,expiresIn:Ys(e.expiresIn),creationTime:Date.now()}}async function kt(e,t){const r=(await t.json()).error;return D.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Nt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function zs(e,{refreshToken:t}){const n=Nt(e);return n.append("Authorization",Js(t)),n}async function Bt(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Ys(e){return Number(e.replace("s","000"))}function Js(e){return`${Dt} ${e}`}/**
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
 */async function Xs({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=Ot(e),s=Nt(e),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:n,authVersion:Dt,appId:e.appId,sdkVersion:Rt},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await Bt(()=>fetch(r,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:Ft(l.authToken)}}else throw await kt("Create Installation",c)}/**
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
 */function Lt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Qs(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Zs=/^[cdef][\w-]{21}$/,ce="";function ea(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=ta(e);return Zs.test(n)?n:ce}catch{return ce}}function ta(e){return Qs(e).substr(0,22)}/**
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
 */function W(e){return`${e.appName}!${e.appId}`}/**
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
 */const jt=new Map;function xt(e,t){const n=W(e);Ht(n,t),na(n,t)}function Ht(e,t){const n=jt.get(e);if(n)for(const r of n)r(t)}function na(e,t){const n=ra();n&&n.postMessage({key:e,fid:t}),sa()}let v=null;function ra(){return!v&&"BroadcastChannel"in self&&(v=new BroadcastChannel("[Firebase] FID Change"),v.onmessage=e=>{Ht(e.data.key,e.data.fid)}),v}function sa(){jt.size===0&&v&&(v.close(),v=null)}/**
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
 */const aa="firebase-installations-database",ia=1,P="firebase-installations-store";let ee=null;function ye(){return ee||(ee=he(aa,ia,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(P)}}})),ee}async function j(e,t){const n=W(e),s=(await ye()).transaction(P,"readwrite"),a=s.objectStore(P),i=await a.get(n);return await a.put(t,n),await s.done,(!i||i.fid!==t.fid)&&xt(e,t.fid),t}async function Vt(e){const t=W(e),r=(await ye()).transaction(P,"readwrite");await r.objectStore(P).delete(t),await r.done}async function K(e,t){const n=W(e),s=(await ye()).transaction(P,"readwrite"),a=s.objectStore(P),i=await a.get(n),o=t(i);return o===void 0?await a.delete(n):await a.put(o,n),await s.done,o&&(!i||i.fid!==o.fid)&&xt(e,o.fid),o}/**
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
 */async function Ie(e){let t;const n=await K(e.appConfig,r=>{const s=oa(r),a=ca(e,s);return t=a.registrationPromise,a.installationEntry});return n.fid===ce?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function oa(e){const t=e||{fid:ea(),registrationStatus:0};return Ut(t)}function ca(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(D.create("app-offline"));return{installationEntry:t,registrationPromise:s}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=la(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:ua(e)}:{installationEntry:t}}async function la(e,t){try{const n=await Xs(e,t);return j(e.appConfig,n)}catch(n){throw Pt(n)&&n.customData.serverCode===409?await Vt(e.appConfig):await j(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function ua(e){let t=await Ue(e.appConfig);for(;t.registrationStatus===1;)await Lt(100),t=await Ue(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await Ie(e);return r||n}return t}function Ue(e){return K(e,t=>{if(!t)throw D.create("installation-not-found");return Ut(t)})}function Ut(e){return ha(e)?{fid:e.fid,registrationStatus:0}:e}function ha(e){return e.registrationStatus===1&&e.registrationTime+Mt<Date.now()}/**
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
 */async function da({appConfig:e,heartbeatServiceProvider:t},n){const r=fa(e,n),s=zs(e,n),a=t.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:Rt,appId:e.appId}},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await Bt(()=>fetch(r,o));if(c.ok){const l=await c.json();return Ft(l)}else throw await kt("Generate Auth Token",c)}function fa(e,{fid:t}){return`${Ot(e)}/${t}/authTokens:generate`}/**
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
 */async function Te(e,t=!1){let n;const r=await K(e.appConfig,a=>{if(!qt(a))throw D.create("not-registered");const i=a.authToken;if(!t&&ma(i))return a;if(i.requestStatus===1)return n=ga(e,t),a;{if(!navigator.onLine)throw D.create("app-offline");const o=wa(a);return n=pa(e,o),o}});return n?await n:r.authToken}async function ga(e,t){let n=await qe(e.appConfig);for(;n.authToken.requestStatus===1;)await Lt(100),n=await qe(e.appConfig);const r=n.authToken;return r.requestStatus===0?Te(e,t):r}function qe(e){return K(e,t=>{if(!qt(t))throw D.create("not-registered");const n=t.authToken;return ya(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function pa(e,t){try{const n=await da(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await j(e.appConfig,r),n}catch(n){if(Pt(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await Vt(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await j(e.appConfig,r)}throw n}}function qt(e){return e!==void 0&&e.registrationStatus===2}function ma(e){return e.requestStatus===2&&!ba(e)}function ba(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+qs}function wa(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function ya(e){return e.requestStatus===1&&e.requestTime+Mt<Date.now()}/**
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
 */async function Ia(e){const t=e,{installationEntry:n,registrationPromise:r}=await Ie(t);return r?r.catch(console.error):Te(t).catch(console.error),n.fid}/**
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
 */async function Ta(e,t=!1){const n=e;return await Sa(n),(await Te(n,t)).token}async function Sa(e){const{registrationPromise:t}=await Ie(e);t&&await t}/**
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
 */function Ea(e){if(!e||!e.options)throw te("App Configuration");if(!e.name)throw te("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw te(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function te(e){return D.create("missing-app-config-values",{valueName:e})}/**
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
 */const Wt="installations",_a="installations-internal",Aa=e=>{const t=e.getProvider("app").getImmediate(),n=Ea(t),r=H(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Ca=e=>{const t=e.getProvider("app").getImmediate(),n=H(t,Wt).getImmediate();return{getId:()=>Ia(n),getToken:s=>Ta(n,s)}};function va(){I(new Ve(Wt,Aa,"PUBLIC")),I(new Ve(_a,Ca,"PRIVATE"))}va();y($t,we);y($t,we,"esm2017");const ne="@firebase/remote-config",We="0.5.0";/**
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
 */const $a="remote-config",Ke=100;/**
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
 */const Ma={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},p=new Ct("remoteconfig","Remote Config",Ma);function Ra(e){const t=Ls(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class Da{constructor(t,n,r,s){this.client=t,this.storage=n,this.storageCache=r,this.logger=s}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,s=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${s}.`),s}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const s=await this.client.fetch(t),a=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&a.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(a),s}}/**
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
 */function Pa(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class Oa{constructor(t,n,r,s,a,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=s,this.apiKey=a,this.appId=i}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:Pa(),custom_signals:t.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(a,c),h=new Promise((w,E)=>{t.signal.addEventListener(()=>{const Se=new Error("The operation was aborted.");Se.name="AbortError",E(Se)})});let d;try{await Promise.race([l,h]),d=await l}catch(w){let E="fetch-client-network";throw(w==null?void 0:w.name)==="AbortError"&&(E="fetch-timeout"),p.create(E,{originalErrorMessage:w==null?void 0:w.message})}let f=d.status;const g=d.headers.get("ETag")||void 0;let S,O;if(d.status===200){let w;try{w=await d.json()}catch(E){throw p.create("fetch-client-parse",{originalErrorMessage:E==null?void 0:E.message})}S=w.entries,O=w.state}if(O==="INSTANCE_STATE_UNSPECIFIED"?f=500:O==="NO_CHANGE"?f=304:(O==="NO_TEMPLATE"||O==="EMPTY_CONFIG")&&(S={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:S}}}/**
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
 */function Fa(e,t){return new Promise((n,r)=>{const s=Math.max(t-Date.now(),0),a=setTimeout(n,s);e.addEventListener(()=>{clearTimeout(a),r(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function ka(e){if(!(e instanceof _t)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Na{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await Fa(t.signal,n);try{const s=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!ka(s))throw s;const a={throttleEndTimeMillis:Date.now()+Bs(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(a),this.attemptFetch(t,a)}}}/**
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
 */const Ba=60*1e3,La=12*60*60*1e3;class ja{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(t,n,r,s,a){this.app=t,this._client=n,this._storageCache=r,this._storage=s,this._logger=a,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Ba,minimumFetchIntervalMillis:La},this.defaultConfig={}}}/**
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
 */function B(e,t){const n=e.target.error||void 0;return p.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const _="app_namespace_store",xa="firebase_remote_config",Ha=1;function Va(){return new Promise((e,t)=>{try{const n=indexedDB.open(xa,Ha);n.onerror=r=>{t(B(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const s=r.target.result;switch(r.oldVersion){case 0:s.createObjectStore(_,{keyPath:"compositeKey"})}}}catch(n){t(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class Ua{constructor(t,n,r,s=Va()){this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=s}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}async setCustomSignals(t){const r=(await this.openDbPromise).transaction([_],"readwrite"),s=await this.getWithTransaction("custom_signals",r),a=Object.assign(Object.assign({},s),t),i=Object.fromEntries(Object.entries(a).filter(([o,c])=>c!==null).map(([o,c])=>typeof c=="number"?[o,c.toString()]:[o,c]));if(Object.keys(i).length>Ke)throw p.create("custom-signal-max-allowed-signals",{maxSignals:Ke});return await this.setWithTransaction("custom_signals",i,r),i}async getWithTransaction(t,n){return new Promise((r,s)=>{const a=n.objectStore(_),i=this.createCompositeKey(t);try{const o=a.get(i);o.onerror=c=>{s(B(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;r(l?l.value:void 0)}}catch(o){s(p.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async setWithTransaction(t,n,r){return new Promise((s,a)=>{const i=r.objectStore(_),o=this.createCompositeKey(t);try{const c=i.put({compositeKey:o,value:n});c.onerror=l=>{a(B(l,"storage-set"))},c.onsuccess=()=>{s()}}catch(c){a(p.create("storage-set",{originalErrorMessage:c==null?void 0:c.message}))}})}async get(t){const r=(await this.openDbPromise).transaction([_],"readonly");return this.getWithTransaction(t,r)}async set(t,n){const s=(await this.openDbPromise).transaction([_],"readwrite");return this.setWithTransaction(t,n,s)}async delete(t){const n=await this.openDbPromise;return new Promise((r,s)=>{const i=n.transaction([_],"readwrite").objectStore(_),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{s(B(l,"storage-delete"))},c.onsuccess=()=>{r()}}catch(c){s(p.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class qa{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),s=this.storage.getCustomSignals(),a=await t;a&&(this.lastFetchStatus=a);const i=await n;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await r;o&&(this.activeConfig=o);const c=await s;c&&(this.customSignals=c)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}async setCustomSignals(t){this.customSignals=await this.storage.setCustomSignals(t)}}/**
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
 */function Wa(){I(new js($a,e,"PUBLIC").setMultipleInstances(!0)),y(ne,We),y(ne,We,"esm2017");function e(t,{instanceIdentifier:n}){const r=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!Ms())throw p.create("indexed-db-unavailable");const{projectId:a,apiKey:i,appId:o}=r.options;if(!a)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!o)throw p.create("registration-app-id");n=n||"firebase";const c=new Ua(o,r.name,n),l=new qa(c),h=new le(ne);h.logLevel=u.ERROR;const d=new Oa(s,tr,n,a,i,o),f=new Na(d,c),g=new Da(f,c,l,h),S=new ja(r,g,l,c,h);return Ra(S),S}}Wa();const Ka=e=>Object.fromEntries(new URLSearchParams(e)),Ga=()=>{const e=Kt(),t=Ka(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},ti=()=>{const[e,t]=re.useState({});return re.useEffect(()=>{const n=setInterval(()=>{},1e3);return()=>clearInterval(n)},[]),e},ni=()=>{const e=Ga();return{logEvent:re.useCallback((n,r)=>{},[e])}};export{ti as a,ni as u};
