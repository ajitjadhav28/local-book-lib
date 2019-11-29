(this["webpackJsonpbook-library"]=this["webpackJsonpbook-library"]||[]).push([[0],{100:function(e,t,a){},103:function(e,t){},105:function(e,t){},140:function(e,t){},141:function(e,t){},202:function(e,t,a){"use strict";a.r(t);var n=a(0),r=a.n(n),s=a(90),c=a.n(s),o=(a(99),a(100),a(91)),l=a(27),i=a(28),p=a(30),u=a(29),m=a(13),b=a(31);a(92);var d=function(e){function t(e){var a;return Object(l.a)(this,t),(a=Object(p.a)(this,Object(u.a)(t).call(this,e))).state={value:"",typing:!1,typingTimeout:0},a.handleChange=a.handleChange.bind(Object(m.a)(a)),a.handleSubmit=a.handleSubmit.bind(Object(m.a)(a)),a}return Object(b.a)(t,e),Object(i.a)(t,[{key:"handleChange",value:function(e){var t=this;this.setState({value:e.target.value}),this.state.typingTimeout&&clearTimeout(this.state.typingTimeout),this.setState({value:e.target.value,typing:!1,typingTimeout:setTimeout((function(){t.props.callback(t.state.value,!1)}),200)})}},{key:"handleSubmit",value:function(e){this.state.value.length>0&&this.props.callback(this.state.value,!0),e.preventDefault()}},{key:"render",value:function(){return r.a.createElement("form",{className:"search-form",onSubmit:this.handleSubmit},r.a.createElement("input",{className:"search-input",placeholder:"   Search Books",type:"text",value:this.state.value,onChange:this.handleChange}))}}]),t}(r.a.Component),h=a(93),f=a(32),k=a.n(f);function g(e){var t=e.props;return"None"!=t.pdf_url&&"None"!=t.epub_url?r.a.createElement(r.a.Fragment,null,r.a.createElement("a",{className:"book-link-pdf App-link",href:t.pdf_url},"PDF(",(t.pdf_size/1048576).toFixed(2),"MB)"),r.a.createElement("a",{className:"book-link-epub App-link",href:t.epub_url},"EPUB(",(t.epub_size/1048576).toFixed(2),"MB)")):t.pdf_url?r.a.createElement("a",{className:"book-link-pdf App-link",href:e.props.pdf_url},"PDF(",(t.pdf_size/1048576).toFixed(2),"MB)"):t.epub_url?r.a.createElement("a",{className:"book-link-epub App-link",href:e.props.epub_url},"EPUB(",(t.epub_size/1048576).toFixed(2),"MB)"):void 0}var v=function(e){return r.a.createElement("div",{className:"book-card"},r.a.createElement("div",{className:"book-card-img"},null!=e.props.image?r.a.createElement("img",{className:"book-card-img-tag",src:"data:image/jpeg;base64,".concat(e.props.image)}):r.a.createElement("img",{className:"book-card-img-tag",src:e.props.image_url})),r.a.createElement("div",{className:"book-card-details"},r.a.createElement("div",{className:"book-card-tite"},r.a.createElement("span",{className:"card-span-title"}," ",e.props.title," ")),r.a.createElement("div",{className:"book-card-subtitle"}),r.a.createElement("div",{className:"book-card-description"},r.a.createElement("span",{className:"book-desc-span"},e.props.description.length>0?e.props.description:"Book description not available.")),r.a.createElement("div",{className:"book-card-misc"},r.a.createElement("span",{style:{marginLeft:"0px"}},r.a.createElement("b",null,"Author:"),e.props.author.substring(0,20),","),r.a.createElement("span",{style:{marginLeft:"5px"}},r.a.createElement("b",null,"Published:"),e.props.year,","),r.a.createElement("span",{style:{marginLeft:"5px"}},r.a.createElement("b",null,"Pages:"),e.props.pages))),r.a.createElement("div",{className:"book-card-download"},r.a.createElement(g,{props:e.props})))};function E(e,t){var a=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),a.push.apply(a,n)}return a}function O(e){for(var t=1;t<arguments.length;t++){var a=null!=arguments[t]?arguments[t]:{};t%2?E(Object(a),!0).forEach((function(t){Object(o.a)(e,t,a[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(a)):E(Object(a)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(a,t))}))}return e}var y="http://127.0.0.28:9999",j=function(e){function t(e){var a;return Object(l.a)(this,t),(a=Object(p.a)(this,Object(u.a)(t).call(this,e))).state={books:!1,initialBooks:!1,search:""},a.handleSearchCallback=a.handleSearchCallback.bind(Object(m.a)(a)),a}return Object(b.a)(t,e),Object(i.a)(t,[{key:"componentDidMount",value:function(){var e=this;k.a.post(y+"/programming OR operating system OR algorithm OR Data Structures OR science/30").then((function(t){e.setState({books:t.data,initialBooks:t.data})}))}},{key:"handleSearchCallback",value:function(e,t){var a=this;e.length>0?(this.setState({search:e}),t?k.a.post(y+"/"+e).then((function(e){a.setState({books:e.data?e.data:[]})})):k.a.post(y+"/"+e+"/6").then((function(e){a.setState({books:e.data?e.data:[]})}))):this.setState({books:this.state.initialBooks})}},{key:"render",value:function(){return this.state.books?r.a.createElement(r.a.Fragment,null,r.a.createElement("div",{className:"search-wraper"},r.a.createElement(d,{callback:this.handleSearchCallback})),r.a.createElement("div",{className:"book-wraper"},this.state.books.map((function(e){return r.a.createElement(v,{key:Object(h.randomBytes)(10),props:O({},e)})})))):""}}]),t}(r.a.Component);var N=function(){return r.a.createElement("div",{className:"App"},r.a.createElement(j,null))};c.a.render(r.a.createElement(N,null),document.getElementById("root"))},92:function(e,t,a){e.exports=a.p+"static/media/search.fe4159ec.png"},94:function(e,t,a){e.exports=a(202)},99:function(e,t,a){}},[[94,1,2]]]);
//# sourceMappingURL=main.5f025b04.chunk.js.map