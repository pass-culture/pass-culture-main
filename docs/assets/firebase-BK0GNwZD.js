import{r as K}from"./index-ClcD9ViR.js";import"./config-BdqymTTq.js";import{b as lt}from"./index-BwDq52Jj.js";/**
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
 */const Me=function(t){const e=[];let n=0;for(let s=0;s<t.length;s++){let r=t.charCodeAt(s);r<128?e[n++]=r:r<2048?(e[n++]=r>>6|192,e[n++]=r&63|128):(r&64512)===55296&&s+1<t.length&&(t.charCodeAt(s+1)&64512)===56320?(r=65536+((r&1023)<<10)+(t.charCodeAt(++s)&1023),e[n++]=r>>18|240,e[n++]=r>>12&63|128,e[n++]=r>>6&63|128,e[n++]=r&63|128):(e[n++]=r>>12|224,e[n++]=r>>6&63|128,e[n++]=r&63|128)}return e},ut=function(t){const e=[];let n=0,s=0;for(;n<t.length;){const r=t[n++];if(r<128)e[s++]=String.fromCharCode(r);else if(r>191&&r<224){const a=t[n++];e[s++]=String.fromCharCode((r&31)<<6|a&63)}else if(r>239&&r<365){const a=t[n++],i=t[n++],o=t[n++],c=((r&7)<<18|(a&63)<<12|(i&63)<<6|o&63)-65536;e[s++]=String.fromCharCode(55296+(c>>10)),e[s++]=String.fromCharCode(56320+(c&1023))}else{const a=t[n++],i=t[n++];e[s++]=String.fromCharCode((r&15)<<12|(a&63)<<6|i&63)}}return e.join("")},ht={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,s=[];for(let r=0;r<t.length;r+=3){const a=t[r],i=r+1<t.length,o=i?t[r+1]:0,c=r+2<t.length,l=c?t[r+2]:0,d=a>>2,h=(a&3)<<4|o>>4;let f=(o&15)<<2|l>>6,g=l&63;c||(g=64,i||(f=64)),s.push(n[d],n[h],n[f],n[g])}return s.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Me(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):ut(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const n=e?this.charToByteMapWebSafe_:this.charToByteMap_,s=[];for(let r=0;r<t.length;){const a=n[t.charAt(r++)],o=r<t.length?n[t.charAt(r)]:0;++r;const l=r<t.length?n[t.charAt(r)]:64;++r;const h=r<t.length?n[t.charAt(r)]:64;if(++r,a==null||o==null||l==null||h==null)throw new dt;const f=a<<2|o>>4;if(s.push(f),l!==64){const g=o<<4&240|l>>2;if(s.push(g),h!==64){const D=l<<6&192|h;s.push(D)}}}return s},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}};class dt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const ft=function(t){const e=Me(t);return ht.encodeByteArray(e,!0)},Re=function(t){return ft(t).replace(/\./g,"")};function gt(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function Z(){try{return typeof indexedDB=="object"}catch{return!1}}function Pe(){return new Promise((t,e)=>{try{let n=!0;const s="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(s);r.onsuccess=()=>{r.result.close(),n||self.indexedDB.deleteDatabase(s),t(!0)},r.onupgradeneeded=()=>{n=!1},r.onerror=()=>{var a;e(((a=r.error)===null||a===void 0?void 0:a.message)||"")}}catch(n){e(n)}})}function pt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const mt="FirebaseError";class A extends Error{constructor(e,n,s){super(n),this.code=e,this.customData=s,this.name=mt,Object.setPrototypeOf(this,A.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,$.prototype.create)}}class ${constructor(e,n,s){this.service=e,this.serviceName=n,this.errors=s}create(e,...n){const s=n[0]||{},r=`${this.service}/${e}`,a=this.errors[e],i=a?bt(a,s):"Error",o=`${this.serviceName}: ${i} (${r}).`;return new A(r,o,s)}}function bt(t,e){return t.replace(wt,(n,s)=>{const r=e[s];return r!=null?String(r):`<${s}?>`})}const wt=/\{\$([^}]+)}/g;/**
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
 */const yt=1e3,It=2,_t=4*60*60*1e3,St=.5;function z(t,e=yt,n=It){const s=e*Math.pow(n,t),r=Math.round(St*s*(Math.random()-.5)*2);return Math.min(_t,s+r)}/**
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
 */function Oe(t){return t&&t._delegate?t._delegate:t}class v{constructor(e,n,s){this.name=e,this.instanceFactory=n,this.type=s,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
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
 */var u;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(u||(u={}));const Et={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Tt=u.INFO,vt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Ct=(t,e,...n)=>{if(e<t.logLevel)return;const s=new Date().toISOString(),r=vt[e];if(r)console[r](`[${s}]  ${t.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class ee{constructor(e){this.name=e,this._logLevel=Tt,this._logHandler=Ct,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in u))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Et[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...e),this._logHandler(this,u.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...e),this._logHandler(this,u.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,u.INFO,...e),this._logHandler(this,u.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,u.WARN,...e),this._logHandler(this,u.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...e),this._logHandler(this,u.ERROR,...e)}}const At=(t,e)=>e.some(n=>t instanceof n);let le,ue;function Dt(){return le||(le=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Mt(){return ue||(ue=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Fe=new WeakMap,Y=new WeakMap,$e=new WeakMap,x=new WeakMap,te=new WeakMap;function Rt(t){const e=new Promise((n,s)=>{const r=()=>{t.removeEventListener("success",a),t.removeEventListener("error",i)},a=()=>{n(T(t.result)),r()},i=()=>{s(t.error),r()};t.addEventListener("success",a),t.addEventListener("error",i)});return e.then(n=>{n instanceof IDBCursor&&Fe.set(n,t)}).catch(()=>{}),te.set(e,t),e}function Pt(t){if(Y.has(t))return;const e=new Promise((n,s)=>{const r=()=>{t.removeEventListener("complete",a),t.removeEventListener("error",i),t.removeEventListener("abort",i)},a=()=>{n(),r()},i=()=>{s(t.error||new DOMException("AbortError","AbortError")),r()};t.addEventListener("complete",a),t.addEventListener("error",i),t.addEventListener("abort",i)});Y.set(t,e)}let J={get(t,e,n){if(t instanceof IDBTransaction){if(e==="done")return Y.get(t);if(e==="objectStoreNames")return t.objectStoreNames||$e.get(t);if(e==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return T(t[e])},set(t,e,n){return t[e]=n,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Ot(t){J=t(J)}function Ft(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...n){const s=t.call(j(this),e,...n);return $e.set(s,e.sort?e.sort():[e]),T(s)}:Mt().includes(t)?function(...e){return t.apply(j(this),e),T(Fe.get(this))}:function(...e){return T(t.apply(j(this),e))}}function $t(t){return typeof t=="function"?Ft(t):(t instanceof IDBTransaction&&Pt(t),At(t,Dt())?new Proxy(t,J):t)}function T(t){if(t instanceof IDBRequest)return Rt(t);if(x.has(t))return x.get(t);const e=$t(t);return e!==t&&(x.set(t,e),te.set(e,t)),e}const j=t=>te.get(t);function Be(t,e,{blocked:n,upgrade:s,blocking:r,terminated:a}={}){const i=indexedDB.open(t,e),o=T(i);return s&&i.addEventListener("upgradeneeded",c=>{s(T(i.result),c.oldVersion,c.newVersion,T(i.transaction),c)}),n&&i.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),o.then(c=>{a&&c.addEventListener("close",()=>a()),r&&c.addEventListener("versionchange",l=>r(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const Bt=["get","getKey","getAll","getAllKeys","count"],Lt=["put","add","delete","clear"],H=new Map;function he(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(H.get(e))return H.get(e);const n=e.replace(/FromIndex$/,""),s=e!==n,r=Lt.includes(n);if(!(n in(s?IDBIndex:IDBObjectStore).prototype)||!(r||Bt.includes(n)))return;const a=async function(i,...o){const c=this.transaction(i,r?"readwrite":"readonly");let l=c.store;return s&&(l=l.index(o.shift())),(await Promise.all([l[n](...o),r&&c.done]))[0]};return H.set(e,a),a}Ot(t=>({...t,get:(e,n,s)=>he(e,n)||t.get(e,n,s),has:(e,n)=>!!he(e,n)||t.has(e,n)}));/**
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
 */class Nt{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(kt(n)){const s=n.getImmediate();return`${s.library}/${s.version}`}else return null}).filter(n=>n).join(" ")}}function kt(t){const e=t.getComponent();return(e==null?void 0:e.type)==="VERSION"}const X="@firebase/app",de="0.11.5";/**
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
 */const I=new ee("@firebase/app"),xt="@firebase/app-compat",jt="@firebase/analytics-compat",Ht="@firebase/analytics",Vt="@firebase/app-check-compat",Ut="@firebase/app-check",Wt="@firebase/auth",qt="@firebase/auth-compat",Gt="@firebase/database",Kt="@firebase/data-connect",zt="@firebase/database-compat",Yt="@firebase/functions",Jt="@firebase/functions-compat",Xt="@firebase/installations",Qt="@firebase/installations-compat",Zt="@firebase/messaging",en="@firebase/messaging-compat",tn="@firebase/performance",nn="@firebase/performance-compat",sn="@firebase/remote-config",rn="@firebase/remote-config-compat",an="@firebase/storage",on="@firebase/storage-compat",cn="@firebase/firestore",ln="@firebase/vertexai",un="@firebase/firestore-compat",hn="firebase",dn="11.6.1",fn={[X]:"fire-core",[xt]:"fire-core-compat",[Ht]:"fire-analytics",[jt]:"fire-analytics-compat",[Ut]:"fire-app-check",[Vt]:"fire-app-check-compat",[Wt]:"fire-auth",[qt]:"fire-auth-compat",[Gt]:"fire-rtdb",[Kt]:"fire-data-connect",[zt]:"fire-rtdb-compat",[Yt]:"fire-fn",[Jt]:"fire-fn-compat",[Xt]:"fire-iid",[Qt]:"fire-iid-compat",[Zt]:"fire-fcm",[en]:"fire-fcm-compat",[tn]:"fire-perf",[nn]:"fire-perf-compat",[sn]:"fire-rc",[rn]:"fire-rc-compat",[an]:"fire-gcs",[on]:"fire-gcs-compat",[cn]:"fire-fst",[un]:"fire-fst-compat",[ln]:"fire-vertex","fire-js":"fire-js",[hn]:"fire-js-all"};/**
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
 */const gn=new Map,pn=new Map,fe=new Map;function ge(t,e){try{t.container.addComponent(e)}catch(n){I.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,n)}}function C(t){const e=t.name;if(fe.has(e))return I.debug(`There were multiple attempts to register component ${e}.`),!1;fe.set(e,t);for(const n of gn.values())ge(n,t);for(const n of pn.values())ge(n,t);return!0}function Le(t,e){const n=t.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const mn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},ne=new $("app","Firebase",mn);/**
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
 */const bn=dn;function y(t,e,n){var s;let r=(s=fn[t])!==null&&s!==void 0?s:t;n&&(r+=`-${n}`);const a=r.match(/\s|\//),i=e.match(/\s|\//);if(a||i){const o=[`Unable to register library "${r}" with version "${e}":`];a&&o.push(`library name "${r}" contains illegal characters (whitespace or "/")`),a&&i&&o.push("and"),i&&o.push(`version name "${e}" contains illegal characters (whitespace or "/")`),I.warn(o.join(" "));return}C(new v(`${r}-version`,()=>({library:r,version:e}),"VERSION"))}/**
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
 */const wn="firebase-heartbeat-database",yn=1,F="firebase-heartbeat-store";let V=null;function Ne(){return V||(V=Be(wn,yn,{upgrade:(t,e)=>{switch(e){case 0:try{t.createObjectStore(F)}catch(n){console.warn(n)}}}}).catch(t=>{throw ne.create("idb-open",{originalErrorMessage:t.message})})),V}async function In(t){try{const n=(await Ne()).transaction(F),s=await n.objectStore(F).get(ke(t));return await n.done,s}catch(e){if(e instanceof A)I.warn(e.message);else{const n=ne.create("idb-get",{originalErrorMessage:e==null?void 0:e.message});I.warn(n.message)}}}async function pe(t,e){try{const s=(await Ne()).transaction(F,"readwrite");await s.objectStore(F).put(e,ke(t)),await s.done}catch(n){if(n instanceof A)I.warn(n.message);else{const s=ne.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});I.warn(s.message)}}}function ke(t){return`${t.name}!${t.options.appId}`}/**
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
 */const _n=1024,Sn=30;class En{constructor(e){this.container=e,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new vn(n),this._heartbeatsCachePromise=this._storage.read().then(s=>(this._heartbeatsCache=s,s))}async triggerHeartbeat(){var e,n;try{const r=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),a=me();if(((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===a||this._heartbeatsCache.heartbeats.some(i=>i.date===a))return;if(this._heartbeatsCache.heartbeats.push({date:a,agent:r}),this._heartbeatsCache.heartbeats.length>Sn){const i=Cn(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(i,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(s){I.warn(s)}}async getHeartbeatsHeader(){var e;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=me(),{heartbeatsToSend:s,unsentEntries:r}=Tn(this._heartbeatsCache.heartbeats),a=Re(JSON.stringify({version:2,heartbeats:s}));return this._heartbeatsCache.lastSentHeartbeatDate=n,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),a}catch(n){return I.warn(n),""}}}function me(){return new Date().toISOString().substring(0,10)}function Tn(t,e=_n){const n=[];let s=t.slice();for(const r of t){const a=n.find(i=>i.agent===r.agent);if(a){if(a.dates.push(r.date),be(n)>e){a.dates.pop();break}}else if(n.push({agent:r.agent,dates:[r.date]}),be(n)>e){n.pop();break}s=s.slice(1)}return{heartbeatsToSend:n,unsentEntries:s}}class vn{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Z()?Pe().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await In(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return pe(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return pe(this.app,{lastSentHeartbeatDate:(n=e.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:[...r.heartbeats,...e.heartbeats]})}else return}}function be(t){return Re(JSON.stringify({version:2,heartbeats:t})).length}function Cn(t){if(t.length===0)return-1;let e=0,n=t[0].date;for(let s=1;s<t.length;s++)t[s].date<n&&(n=t[s].date,e=s);return e}/**
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
 */function An(t){C(new v("platform-logger",e=>new Nt(e),"PRIVATE")),C(new v("heartbeat",e=>new En(e),"PRIVATE")),y(X,de,t),y(X,de,"esm2017"),y("fire-js","")}An("");const xe="@firebase/installations",se="0.6.13";/**
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
 */const je=1e4,He=`w:${se}`,Ve="FIS_v2",Dn="https://firebaseinstallations.googleapis.com/v1",Mn=60*60*1e3,Rn="installations",Pn="Installations";/**
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
 */const On={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},R=new $(Rn,Pn,On);function Ue(t){return t instanceof A&&t.code.includes("request-failed")}/**
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
 */function We({projectId:t}){return`${Dn}/projects/${t}/installations`}function qe(t){return{token:t.token,requestStatus:2,expiresIn:$n(t.expiresIn),creationTime:Date.now()}}async function Ge(t,e){const s=(await e.json()).error;return R.create("request-failed",{requestName:t,serverCode:s.code,serverMessage:s.message,serverStatus:s.status})}function Ke({apiKey:t}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":t})}function Fn(t,{refreshToken:e}){const n=Ke(t);return n.append("Authorization",Bn(e)),n}async function ze(t){const e=await t();return e.status>=500&&e.status<600?t():e}function $n(t){return Number(t.replace("s","000"))}function Bn(t){return`${Ve} ${t}`}/**
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
 */async function Ln({appConfig:t,heartbeatServiceProvider:e},{fid:n}){const s=We(t),r=Ke(t),a=e.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={fid:n,authVersion:Ve,appId:t.appId,sdkVersion:He},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await ze(()=>fetch(s,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:qe(l.authToken)}}else throw await Ge("Create Installation",c)}/**
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
 */function Ye(t){return new Promise(e=>{setTimeout(e,t)})}/**
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
 */function Nn(t){return btoa(String.fromCharCode(...t)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const kn=/^[cdef][\w-]{21}$/,Q="";function xn(){try{const t=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(t),t[0]=112+t[0]%16;const n=jn(t);return kn.test(n)?n:Q}catch{return Q}}function jn(t){return Nn(t).substr(0,22)}/**
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
 */function N(t){return`${t.appName}!${t.appId}`}/**
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
 */const Je=new Map;function Xe(t,e){const n=N(t);Qe(n,e),Hn(n,e)}function Qe(t,e){const n=Je.get(t);if(n)for(const s of n)s(e)}function Hn(t,e){const n=Vn();n&&n.postMessage({key:t,fid:e}),Un()}let M=null;function Vn(){return!M&&"BroadcastChannel"in self&&(M=new BroadcastChannel("[Firebase] FID Change"),M.onmessage=t=>{Qe(t.data.key,t.data.fid)}),M}function Un(){Je.size===0&&M&&(M.close(),M=null)}/**
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
 */const Wn="firebase-installations-database",qn=1,P="firebase-installations-store";let U=null;function re(){return U||(U=Be(Wn,qn,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(P)}}})),U}async function L(t,e){const n=N(t),r=(await re()).transaction(P,"readwrite"),a=r.objectStore(P),i=await a.get(n);return await a.put(e,n),await r.done,(!i||i.fid!==e.fid)&&Xe(t,e.fid),e}async function Ze(t){const e=N(t),s=(await re()).transaction(P,"readwrite");await s.objectStore(P).delete(e),await s.done}async function k(t,e){const n=N(t),r=(await re()).transaction(P,"readwrite"),a=r.objectStore(P),i=await a.get(n),o=e(i);return o===void 0?await a.delete(n):await a.put(o,n),await r.done,o&&(!i||i.fid!==o.fid)&&Xe(t,o.fid),o}/**
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
 */async function ae(t){let e;const n=await k(t.appConfig,s=>{const r=Gn(s),a=Kn(t,r);return e=a.registrationPromise,a.installationEntry});return n.fid===Q?{installationEntry:await e}:{installationEntry:n,registrationPromise:e}}function Gn(t){const e=t||{fid:xn(),registrationStatus:0};return et(e)}function Kn(t,e){if(e.registrationStatus===0){if(!navigator.onLine){const r=Promise.reject(R.create("app-offline"));return{installationEntry:e,registrationPromise:r}}const n={fid:e.fid,registrationStatus:1,registrationTime:Date.now()},s=zn(t,n);return{installationEntry:n,registrationPromise:s}}else return e.registrationStatus===1?{installationEntry:e,registrationPromise:Yn(t)}:{installationEntry:e}}async function zn(t,e){try{const n=await Ln(t,e);return L(t.appConfig,n)}catch(n){throw Ue(n)&&n.customData.serverCode===409?await Ze(t.appConfig):await L(t.appConfig,{fid:e.fid,registrationStatus:0}),n}}async function Yn(t){let e=await we(t.appConfig);for(;e.registrationStatus===1;)await Ye(100),e=await we(t.appConfig);if(e.registrationStatus===0){const{installationEntry:n,registrationPromise:s}=await ae(t);return s||n}return e}function we(t){return k(t,e=>{if(!e)throw R.create("installation-not-found");return et(e)})}function et(t){return Jn(t)?{fid:t.fid,registrationStatus:0}:t}function Jn(t){return t.registrationStatus===1&&t.registrationTime+je<Date.now()}/**
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
 */async function Xn({appConfig:t,heartbeatServiceProvider:e},n){const s=Qn(t,n),r=Fn(t,n),a=e.getImmediate({optional:!0});if(a){const l=await a.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={installation:{sdkVersion:He,appId:t.appId}},o={method:"POST",headers:r,body:JSON.stringify(i)},c=await ze(()=>fetch(s,o));if(c.ok){const l=await c.json();return qe(l)}else throw await Ge("Generate Auth Token",c)}function Qn(t,{fid:e}){return`${We(t)}/${e}/authTokens:generate`}/**
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
 */async function ie(t,e=!1){let n;const s=await k(t.appConfig,a=>{if(!tt(a))throw R.create("not-registered");const i=a.authToken;if(!e&&ts(i))return a;if(i.requestStatus===1)return n=Zn(t,e),a;{if(!navigator.onLine)throw R.create("app-offline");const o=ss(a);return n=es(t,o),o}});return n?await n:s.authToken}async function Zn(t,e){let n=await ye(t.appConfig);for(;n.authToken.requestStatus===1;)await Ye(100),n=await ye(t.appConfig);const s=n.authToken;return s.requestStatus===0?ie(t,e):s}function ye(t){return k(t,e=>{if(!tt(e))throw R.create("not-registered");const n=e.authToken;return rs(n)?Object.assign(Object.assign({},e),{authToken:{requestStatus:0}}):e})}async function es(t,e){try{const n=await Xn(t,e),s=Object.assign(Object.assign({},e),{authToken:n});return await L(t.appConfig,s),n}catch(n){if(Ue(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await Ze(t.appConfig);else{const s=Object.assign(Object.assign({},e),{authToken:{requestStatus:0}});await L(t.appConfig,s)}throw n}}function tt(t){return t!==void 0&&t.registrationStatus===2}function ts(t){return t.requestStatus===2&&!ns(t)}function ns(t){const e=Date.now();return e<t.creationTime||t.creationTime+t.expiresIn<e+Mn}function ss(t){const e={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},t),{authToken:e})}function rs(t){return t.requestStatus===1&&t.requestTime+je<Date.now()}/**
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
 */async function as(t){const e=t,{installationEntry:n,registrationPromise:s}=await ae(e);return s?s.catch(console.error):ie(e).catch(console.error),n.fid}/**
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
 */async function is(t,e=!1){const n=t;return await os(n),(await ie(n,e)).token}async function os(t){const{registrationPromise:e}=await ae(t);e&&await e}/**
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
 */function cs(t){if(!t||!t.options)throw W("App Configuration");if(!t.name)throw W("App Name");const e=["projectId","apiKey","appId"];for(const n of e)if(!t.options[n])throw W(n);return{appName:t.name,projectId:t.options.projectId,apiKey:t.options.apiKey,appId:t.options.appId}}function W(t){return R.create("missing-app-config-values",{valueName:t})}/**
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
 */const nt="installations",ls="installations-internal",us=t=>{const e=t.getProvider("app").getImmediate(),n=cs(e),s=Le(e,"heartbeat");return{app:e,appConfig:n,heartbeatServiceProvider:s,_delete:()=>Promise.resolve()}},hs=t=>{const e=t.getProvider("app").getImmediate(),n=Le(e,nt).getImmediate();return{getId:()=>as(n),getToken:r=>is(n,r)}};function ds(){C(new v(nt,us,"PUBLIC")),C(new v(ls,hs,"PRIVATE"))}ds();y(xe,se);y(xe,se,"esm2017");/**
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
 */const Ie="analytics",fs="firebase_id",gs="origin",ps=60*1e3,ms="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",oe="https://www.googletagmanager.com/gtag/js";/**
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
 */const p=new ee("@firebase/analytics");/**
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
 */const bs={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},b=new $("analytics","Analytics",bs);/**
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
 */function ws(t){if(!t.startsWith(oe)){const e=b.create("invalid-gtag-resource",{gtagURL:t});return p.warn(e.message),""}return t}function st(t){return Promise.all(t.map(e=>e.catch(n=>n)))}function ys(t,e){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(t,e)),n}function Is(t,e){const n=ys("firebase-js-sdk-policy",{createScriptURL:ws}),s=document.createElement("script"),r=`${oe}?l=${t}&id=${e}`;s.src=n?n==null?void 0:n.createScriptURL(r):r,s.async=!0,document.head.appendChild(s)}function _s(t){let e=[];return Array.isArray(window[t])?e=window[t]:window[t]=e,e}async function Ss(t,e,n,s,r,a){const i=s[r];try{if(i)await e[i];else{const c=(await st(n)).find(l=>l.measurementId===r);c&&await e[c.appId]}}catch(o){p.error(o)}t("config",r,a)}async function Es(t,e,n,s,r){try{let a=[];if(r&&r.send_to){let i=r.send_to;Array.isArray(i)||(i=[i]);const o=await st(n);for(const c of i){const l=o.find(h=>h.measurementId===c),d=l&&e[l.appId];if(d)a.push(d);else{a=[];break}}}a.length===0&&(a=Object.values(e)),await Promise.all(a),t("event",s,r||{})}catch(a){p.error(a)}}function Ts(t,e,n,s){async function r(a,...i){try{if(a==="event"){const[o,c]=i;await Es(t,e,n,o,c)}else if(a==="config"){const[o,c]=i;await Ss(t,e,n,s,o,c)}else if(a==="consent"){const[o,c]=i;t("consent",o,c)}else if(a==="get"){const[o,c,l]=i;t("get",o,c,l)}else if(a==="set"){const[o]=i;t("set",o)}else t(a,...i)}catch(o){p.error(o)}}return r}function vs(t,e,n,s,r){let a=function(...i){window[s].push(arguments)};return window[r]&&typeof window[r]=="function"&&(a=window[r]),window[r]=Ts(a,t,e,n),{gtagCore:a,wrappedGtag:window[r]}}function Cs(t){const e=window.document.getElementsByTagName("script");for(const n of Object.values(e))if(n.src&&n.src.includes(oe)&&n.src.includes(t))return n;return null}/**
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
 */const As=30,Ds=1e3;class Ms{constructor(e={},n=Ds){this.throttleMetadata=e,this.intervalMillis=n}getThrottleMetadata(e){return this.throttleMetadata[e]}setThrottleMetadata(e,n){this.throttleMetadata[e]=n}deleteThrottleMetadata(e){delete this.throttleMetadata[e]}}const rt=new Ms;function Rs(t){return new Headers({Accept:"application/json","x-goog-api-key":t})}async function Ps(t){var e;const{appId:n,apiKey:s}=t,r={method:"GET",headers:Rs(s)},a=ms.replace("{app-id}",n),i=await fetch(a,r);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((e=c.error)===null||e===void 0)&&e.message&&(o=c.error.message)}catch{}throw b.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function Os(t,e=rt,n){const{appId:s,apiKey:r,measurementId:a}=t.options;if(!s)throw b.create("no-app-id");if(!r){if(a)return{measurementId:a,appId:s};throw b.create("no-api-key")}const i=e.getThrottleMetadata(s)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new Bs;return setTimeout(async()=>{o.abort()},ps),at({appId:s,apiKey:r,measurementId:a},i,o,e)}async function at(t,{throttleEndTimeMillis:e,backoffCount:n},s,r=rt){var a;const{appId:i,measurementId:o}=t;try{await Fs(s,e)}catch(c){if(o)return p.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await Ps(t);return r.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!$s(l)){if(r.deleteThrottleMetadata(i),o)return p.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const d=Number((a=l==null?void 0:l.customData)===null||a===void 0?void 0:a.httpStatus)===503?z(n,r.intervalMillis,As):z(n,r.intervalMillis),h={throttleEndTimeMillis:Date.now()+d,backoffCount:n+1};return r.setThrottleMetadata(i,h),p.debug(`Calling attemptFetch again in ${d} millis`),at(t,h,s,r)}}function Fs(t,e){return new Promise((n,s)=>{const r=Math.max(e-Date.now(),0),a=setTimeout(n,r);t.addEventListener(()=>{clearTimeout(a),s(b.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function $s(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class Bs{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}async function Ls(t,e,n,s,r){if(r&&r.global){t("event",n,s);return}else{const a=await e,i=Object.assign(Object.assign({},s),{send_to:a});t("event",n,i)}}/**
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
 */async function Ns(){if(Z())try{await Pe()}catch(t){return p.warn(b.create("indexeddb-unavailable",{errorInfo:t==null?void 0:t.toString()}).message),!1}else return p.warn(b.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function ks(t,e,n,s,r,a,i){var o;const c=Os(t);c.then(g=>{n[g.measurementId]=g.appId,t.options.measurementId&&g.measurementId!==t.options.measurementId&&p.warn(`The measurement ID in the local Firebase config (${t.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>p.error(g)),e.push(c);const l=Ns().then(g=>{if(g)return s.getId()}),[d,h]=await Promise.all([c,l]);Cs(a)||Is(a,d.measurementId),r("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[gs]="firebase",f.update=!0,h!=null&&(f[fs]=h),r("config",d.measurementId,f),d.measurementId}/**
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
 */class xs{constructor(e){this.app=e}_delete(){return delete O[this.app.options.appId],Promise.resolve()}}let O={},_e=[];const Se={};let q="dataLayer",js="gtag",Ee,it,Te=!1;function Hs(){const t=[];if(gt()&&t.push("This is a browser extension environment."),pt()||t.push("Cookies are not available."),t.length>0){const e=t.map((s,r)=>`(${r+1}) ${s}`).join(" "),n=b.create("invalid-analytics-context",{errorInfo:e});p.warn(n.message)}}function Vs(t,e,n){Hs();const s=t.options.appId;if(!s)throw b.create("no-app-id");if(!t.options.apiKey)if(t.options.measurementId)p.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${t.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw b.create("no-api-key");if(O[s]!=null)throw b.create("already-exists",{id:s});if(!Te){_s(q);const{wrappedGtag:a,gtagCore:i}=vs(O,_e,Se,q,js);it=a,Ee=i,Te=!0}return O[s]=ks(t,_e,Se,e,Ee,q,n),new xs(t)}function Us(t,e,n,s){t=Oe(t),Ls(it,O[t.app.options.appId],e,n,s).catch(r=>p.error(r))}const ve="@firebase/analytics",Ce="0.10.12";function Ws(){C(new v(Ie,(e,{options:n})=>{const s=e.getProvider("app").getImmediate(),r=e.getProvider("installations-internal").getImmediate();return Vs(s,r,n)},"PUBLIC")),C(new v("analytics-internal",t,"PRIVATE")),y(ve,Ce),y(ve,Ce,"esm2017");function t(e){try{const n=e.getProvider(Ie).getImmediate();return{logEvent:(s,r,a)=>Us(n,s,r,a)}}catch(n){throw b.create("interop-component-reg-failed",{reason:n})}}}Ws();const G="@firebase/remote-config",Ae="0.6.0";/**
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
 */const qs="remote-config",De=100;/**
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
 */const Gs={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},m=new $("remoteconfig","Remote Config",Gs);function Ks(t){const e=Oe(t);return e._initializePromise||(e._initializePromise=e._storageCache.loadFromStorage().then(()=>{e._isInitializationComplete=!0})),e._initializePromise}/**
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
 */class zs{constructor(e,n,s,r){this.client=e,this.storage=n,this.storageCache=s,this.logger=r}isCachedDataFresh(e,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const s=Date.now()-n,r=s<=e;return this.logger.debug(`Config fetch cache check. Cache age millis: ${s}. Cache max age millis (minimumFetchIntervalMillis setting): ${e}. Is cache hit: ${r}.`),r}async fetch(e){const[n,s]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(s&&this.isCachedDataFresh(e.cacheMaxAgeMillis,n))return s;e.eTag=s&&s.eTag;const r=await this.client.fetch(e),a=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return r.status===200&&a.push(this.storage.setLastSuccessfulFetchResponse(r)),await Promise.all(a),r}}/**
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
 */function Ys(t=navigator){return t.languages&&t.languages[0]||t.language}/**
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
 */class Js{constructor(e,n,s,r,a,i){this.firebaseInstallations=e,this.sdkVersion=n,this.namespace=s,this.projectId=r,this.apiKey=a,this.appId=i}async fetch(e){const[n,s]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":e.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:s,app_id:this.appId,language_code:Ys(),custom_signals:e.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(a,c),d=new Promise((w,S)=>{e.signal.addEventListener(()=>{const ce=new Error("The operation was aborted.");ce.name="AbortError",S(ce)})});let h;try{await Promise.race([l,d]),h=await l}catch(w){let S="fetch-client-network";throw(w==null?void 0:w.name)==="AbortError"&&(S="fetch-timeout"),m.create(S,{originalErrorMessage:w==null?void 0:w.message})}let f=h.status;const g=h.headers.get("ETag")||void 0;let D,_;if(h.status===200){let w;try{w=await h.json()}catch(S){throw m.create("fetch-client-parse",{originalErrorMessage:S==null?void 0:S.message})}D=w.entries,_=w.state}if(_==="INSTANCE_STATE_UNSPECIFIED"?f=500:_==="NO_CHANGE"?f=304:(_==="NO_TEMPLATE"||_==="EMPTY_CONFIG")&&(D={}),f!==304&&f!==200)throw m.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:D}}}/**
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
 */function Xs(t,e){return new Promise((n,s)=>{const r=Math.max(e-Date.now(),0),a=setTimeout(n,r);t.addEventListener(()=>{clearTimeout(a),s(m.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function Qs(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class Zs{constructor(e,n){this.client=e,this.storage=n}async fetch(e){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(e,n)}async attemptFetch(e,{throttleEndTimeMillis:n,backoffCount:s}){await Xs(e.signal,n);try{const r=await this.client.fetch(e);return await this.storage.deleteThrottleMetadata(),r}catch(r){if(!Qs(r))throw r;const a={throttleEndTimeMillis:Date.now()+z(s),backoffCount:s+1};return await this.storage.setThrottleMetadata(a),this.attemptFetch(e,a)}}}/**
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
 */const er=60*1e3,tr=12*60*60*1e3;class nr{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(e,n,s,r,a){this.app=e,this._client=n,this._storageCache=s,this._storage=r,this._logger=a,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:er,minimumFetchIntervalMillis:tr},this.defaultConfig={}}}/**
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
 */function B(t,e){const n=t.target.error||void 0;return m.create(e,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const E="app_namespace_store",sr="firebase_remote_config",rr=1;function ar(){return new Promise((t,e)=>{try{const n=indexedDB.open(sr,rr);n.onerror=s=>{e(B(s,"storage-open"))},n.onsuccess=s=>{t(s.target.result)},n.onupgradeneeded=s=>{const r=s.target.result;switch(s.oldVersion){case 0:r.createObjectStore(E,{keyPath:"compositeKey"})}}}catch(n){e(m.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class ot{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(e){return this.set("last_fetch_status",e)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(e){return this.set("last_successful_fetch_timestamp_millis",e)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(e){return this.set("last_successful_fetch_response",e)}getActiveConfig(){return this.get("active_config")}setActiveConfig(e){return this.set("active_config",e)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(e){return this.set("active_config_etag",e)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(e){return this.set("throttle_metadata",e)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}}class ir extends ot{constructor(e,n,s,r=ar()){super(),this.appId=e,this.appName=n,this.namespace=s,this.openDbPromise=r}async setCustomSignals(e){const s=(await this.openDbPromise).transaction([E],"readwrite"),r=await this.getWithTransaction("custom_signals",s),a=ct(e,r||{});return await this.setWithTransaction("custom_signals",a,s),a}async getWithTransaction(e,n){return new Promise((s,r)=>{const a=n.objectStore(E),i=this.createCompositeKey(e);try{const o=a.get(i);o.onerror=c=>{r(B(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;s(l?l.value:void 0)}}catch(o){r(m.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async setWithTransaction(e,n,s){return new Promise((r,a)=>{const i=s.objectStore(E),o=this.createCompositeKey(e);try{const c=i.put({compositeKey:o,value:n});c.onerror=l=>{a(B(l,"storage-set"))},c.onsuccess=()=>{r()}}catch(c){a(m.create("storage-set",{originalErrorMessage:c==null?void 0:c.message}))}})}async get(e){const s=(await this.openDbPromise).transaction([E],"readonly");return this.getWithTransaction(e,s)}async set(e,n){const r=(await this.openDbPromise).transaction([E],"readwrite");return this.setWithTransaction(e,n,r)}async delete(e){const n=await this.openDbPromise;return new Promise((s,r)=>{const i=n.transaction([E],"readwrite").objectStore(E),o=this.createCompositeKey(e);try{const c=i.delete(o);c.onerror=l=>{r(B(l,"storage-delete"))},c.onsuccess=()=>{s()}}catch(c){r(m.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(e){return[this.appId,this.appName,this.namespace,e].join()}}class or extends ot{constructor(){super(...arguments),this.storage={}}async get(e){return Promise.resolve(this.storage[e])}async set(e,n){return this.storage[e]=n,Promise.resolve(void 0)}async delete(e){return this.storage[e]=void 0,Promise.resolve()}async setCustomSignals(e){const n=this.storage.custom_signals||{};return this.storage.custom_signals=ct(e,n),Promise.resolve(this.storage.custom_signals)}}function ct(t,e){const n=Object.assign(Object.assign({},e),t),s=Object.fromEntries(Object.entries(n).filter(([r,a])=>a!==null).map(([r,a])=>typeof a=="number"?[r,a.toString()]:[r,a]));if(Object.keys(s).length>De)throw m.create("custom-signal-max-allowed-signals",{maxSignals:De});return s}/**
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
 */class cr{constructor(e){this.storage=e}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const e=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),s=this.storage.getActiveConfig(),r=this.storage.getCustomSignals(),a=await e;a&&(this.lastFetchStatus=a);const i=await n;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await s;o&&(this.activeConfig=o);const c=await r;c&&(this.customSignals=c)}setLastFetchStatus(e){return this.lastFetchStatus=e,this.storage.setLastFetchStatus(e)}setLastSuccessfulFetchTimestampMillis(e){return this.lastSuccessfulFetchTimestampMillis=e,this.storage.setLastSuccessfulFetchTimestampMillis(e)}setActiveConfig(e){return this.activeConfig=e,this.storage.setActiveConfig(e)}async setCustomSignals(e){this.customSignals=await this.storage.setCustomSignals(e)}}/**
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
 */function lr(){C(new v(qs,t,"PUBLIC").setMultipleInstances(!0)),y(G,Ae),y(G,Ae,"esm2017");function t(e,{options:n}){const s=e.getProvider("app").getImmediate(),r=e.getProvider("installations-internal").getImmediate(),{projectId:a,apiKey:i,appId:o}=s.options;if(!a)throw m.create("registration-project-id");if(!i)throw m.create("registration-api-key");if(!o)throw m.create("registration-app-id");const c=(n==null?void 0:n.templateId)||"firebase",l=Z()?new ir(o,s.name,c):new or,d=new cr(l),h=new ee(G);h.logLevel=u.ERROR;const f=new Js(r,bn,c,a,i,o),g=new Zs(f,l),D=new zs(g,l,d,h),_=new nr(s,D,d,l,h);return Ks(_),_}}lr();const ur=t=>Object.fromEntries(new URLSearchParams(t)),hr=()=>{const t=lt(),e=ur(t.search);return"utm_campaign"in e&&"utm_medium"in e&&"utm_source"in e?{traffic_campaign:e.utm_campaign,traffic_medium:e.utm_medium,traffic_source:e.utm_source}:{}},pr=()=>{const[t,e]=K.useState({});return K.useEffect(()=>{const n=setInterval(()=>{},1e3);return()=>clearInterval(n)},[]),t},mr=()=>{const t=hr();return{logEvent:K.useCallback((n,s)=>{},[t])}};export{pr as a,mr as u};
